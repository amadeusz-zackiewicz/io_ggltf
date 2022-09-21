from io_ggltf.Keywords import *
from io_ggltf.Core.Scoops import Node as NodeScoop
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.BlenderUtil import get_object_accessor
from io_ggltf.Advanced import Settings, Linker 
from io_ggltf.Core import Util, BlenderUtil
import bpy

#__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
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

    __auto_parent(bucket, obj, nodeID, parent)

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
            Linker.node_to_node(bucket, c, nodeID)
        
        bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), parent)))
        return nodeID

    obj = try_get_object(topObjAccessor)

    if parent == None:
        parent = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE)

    topNodeID = __recursive(bucket, obj, blacklist, parent, checkRedundancies, filters)

    __auto_parent(bucket, obj, topNodeID, parent)

    return topNodeID


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
    if parent == None:
        parent = Settings.get_setting(bucket, BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)

    collection = bpy.data.collections.get(collectionName)

    topObjects = __get_collection_top_objects(collection)

    nodeIDs = []
    for topObj in topObjects:
        if not topObj.name in blacklist and Util.name_passes_filters(filters, topObj.name):
            nodeIDs.append(based_on_hierarchy(bucket, get_object_accessor(topObj), blacklist, parent, checkRedundancies, filters=filters))

    return nodeIDs

def __auto_parent(bucket: Bucket, childObj, childID, parent):
    if type(parent) == str:
        try:
            parentObj = Util.try_get_object(parent)
        except:
            return
        parent = (parent, None) # this will trigger  == tuple below

    if type(parent) == bool:
        if parent:
            if childObj.parent != None:
                parent = BlenderUtil.get_parent_accessor(childObj) # this will trigger  == tuple below
            else:
                return
        else:
            return

    if type(parent) == int:
        parent = bucket.accessors[BUCKET_DATA_NODES][parent] # this will trigger  == tuple below

    if type(parent) == tuple:
        parentID = __get_parent_id(bucket, parent)
        Linker.node_to_node(bucket, childID, parentID)
        return

    raise Exception(f"Failed to resolve parent for '{BlenderUtil.get_object_accessor(childObj)}', parent accessor was: '{parent}'. Make sure that parent is added before the child")

def __get_parent_id(bucket: Bucket, accessor):
    try:
        id = RM.fetch_unique(bucket, accessor, BUCKET_DATA_NODES)
        return id
    except:
        try:
            id = RM.fetch_last_id_from_unsafe(bucket, accessor, BUCKET_DATA_NODES)
            return id
        except:
            raise Exception(f"{accessor} needs to be added before it's children can access it")