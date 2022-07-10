from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Scoops import Node as NodeScoop
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Util import try_get_object
from io_advanced_gltf2.Core.BlenderUtil import get_object_getter
from io_advanced_gltf2.Core import Linker
from io_advanced_gltf2.Advanced import Settings
import bpy

__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
__scoopCommand = lambda bucket, assignedID, objID, space: NodeScoop.scoop_object(bucket=bucket, assignedID=assignedID, objID=objID, worldSpace=space)

def based_on_object(bucket: Bucket, objName, worldSpace=None, checkRedundancies=None) -> int:

    obj = try_get_object(objName)
    if worldSpace == None:
        worldSpace = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_WORLD_SPACE)

    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    if checkRedundancies:
        redundant, nodeID = RM.smart_redundancy(bucket, get_object_getter(obj), BUCKET_DATA_NODES)
        if redundant:
            return nodeID
        else:
            bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_getter(obj), worldSpace)))
            return nodeID
    else:
        nodeID = RM.reserve_untracked_id(bucket, BUCKET_DATA_NODES)


def based_on_hierarchy(bucket: Bucket, topObjName, blacklist = {}, topObjWorldSpace=None, checkRedundancies=None) -> int:
    def __recursive(bucket: Bucket, obj, blacklist, worldSpace, checkRedundancies):
        if obj.name in blacklist:
            return None

        childrenIDs = []
        if __object_is_collection_instance(obj):
            childrenIDs.extend(based_on_collection(bucket=bucket, collectionName=get_object_getter(obj.instance_collection), blacklist=blacklist, worldSpace=False, checkRedundancies=checkRedundancies))
        else:
            for c in obj.children:
                childID = __recursive(bucket, c, blacklist, False, checkRedundancies)
                if childID != None:
                    childrenIDs.append(childID)

        if checkRedundancies:
            redundant, nodeID = RM.smart_redundancy(bucket, get_object_getter(obj), BUCKET_DATA_NODES)
            if redundant:
                return nodeID
        else:
            nodeID = RM.reserve_untracked_id(bucket, BUCKET_DATA_NODES)

        for c in childrenIDs:
            bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__linkChildCommand, (bucket, nodeID, c)))
        
        bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_getter(obj), worldSpace)))
        return nodeID

    obj = try_get_object(topObjName)

    if topObjWorldSpace == None:
        topObjWorldSpace = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_WORLD_SPACE)

    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    return __recursive(bucket, obj, blacklist, topObjWorldSpace, checkRedundancies)

def __object_is_collection_instance(obj) -> bool:
    return obj.instance_type == BLENDER_INSTANCE_TYPE_COLLECTION

def __get_collection_top_objects(collection, blacklist={}):
    topObjects = []
    for obj in collection.objects:
        if obj.parent == None and not obj.name in blacklist:
            topObjects.append(obj)
    return topObjects

def based_on_collection(bucket: Bucket, collectionName, blacklist={}, worldSpace=None, checkRedundancies=None) -> list:
    if worldSpace == None:
        worldSpace = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_WORLD_SPACE)
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    collection = bpy.data.collections.get(collectionName)

    topObjects = __get_collection_top_objects(collection)

    nodeIDs = []
    for topObj in topObjects:
        nodeIDs.append(based_on_hierarchy(bucket, get_object_getter(topObj), blacklist, worldSpace, checkRedundancies))

    return nodeIDs