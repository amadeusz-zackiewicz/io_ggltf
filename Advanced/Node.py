from io_ggltf.Keywords import *
from io_ggltf.Core.Scoops import Node as NodeScoop
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.BlenderUtil import get_object_accessor
from io_ggltf.Core import Linker
from io_ggltf.Advanced import Settings
from io_ggltf.Core import Util, BlenderUtil
import bpy

__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
__scoopCommand = lambda bucket, assignedID, objID, parent: NodeScoop.scoop_object(bucket=bucket, assignedID=assignedID, objAccessor=objID, parent=parent)

def based_on_object(bucket: Bucket, objAccessor, parent=None, checkRedundancies=None, rename=None) -> int:

    obj = try_get_object(objAccessor)
    if parent == None:
        parent = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)

    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    if checkRedundancies:
        redundant, nodeID = RM.register_unique(bucket, get_object_accessor(obj), BUCKET_DATA_NODES, bpy.data.objects.get)
        if redundant:
            return nodeID
    else:
        nodeID = RM.register_unsafe(bucket, get_object_accessor(obj), BUCKET_DATA_NODES)

    if rename != None:
        if type(rename) == str:
            bucket.commandQueue[COMMAND_QUEUE_NAMING].append((Util.rename_node, (bucket, nodeID, rename)))
        else:
            raise Exception(f"based_on_object: 'rename' is expected to be a string, got {type(rename)} instead.")
        
    bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), parent)))
    return nodeID


def based_on_hierarchy(bucket: Bucket, topObjAccessor, blacklist = {}, parent=None, checkRedundancies=None, filters=[]) -> int:
    def __recursive(bucket: Bucket, obj, blacklist, parent, checkRedundancies, filters):
        if obj.name in blacklist or not Util.name_passes_filters(filters, obj.name):
            return None

        childrenIDs = []
        if __object_is_collection_instance(obj):
            childrenIDs.extend(based_on_collection(bucket=bucket, collectionName=get_object_accessor(obj.instance_collection), blacklist=blacklist, parent=True, checkRedundancies=checkRedundancies))
        else:
            for c in obj.children:
                childID = __recursive(bucket, c, blacklist, True, checkRedundancies, filters)
                if childID != None:
                    childrenIDs.append(childID)

        if checkRedundancies:
            redundant, nodeID = RM.register_unique(bucket, get_object_accessor(obj), BUCKET_DATA_NODES, bpy.data.objects.get)
            if redundant:
                return nodeID
        else:
            nodeID = RM.register_unsafe(bucket, get_object_accessor(obj), BUCKET_DATA_NODES)

        for c in childrenIDs:
            bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__linkChildCommand, (bucket, nodeID, c)))
        
        bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), parent)))
        return nodeID

    obj = try_get_object(topObjAccessor)

    if parent == None:
        parent = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    if type(parent) != bool:
        parent = try_get_object(parent)

    return __recursive(bucket, obj, blacklist, parent, checkRedundancies, filters)


def __object_is_collection_instance(obj) -> bool:
    return obj.instance_type == BLENDER_INSTANCE_TYPE_COLLECTION

def __get_collection_top_objects(collection, blacklist={}):
    topObjects = []
    for obj in collection.objects:
        if obj.parent == None and not obj.name in blacklist:
            topObjects.append(obj)
    return topObjects

def based_on_collection(bucket: Bucket, collectionName, blacklist={}, parent=None, checkRedundancies=None, filters=[]) -> list:
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    collection = bpy.data.collections.get(collectionName)

    topObjects = __get_collection_top_objects(collection)

    nodeIDs = []
    for topObj in topObjects:
        if not topObj.name in blacklist and Util.name_passes_filters(filters, topObj.name):
            nodeIDs.append(based_on_hierarchy(bucket, get_object_accessor(topObj), blacklist, parent, checkRedundancies, filters=filters))

    return nodeIDs