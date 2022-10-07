from io_ggltf import Keywords as __k
from io_ggltf.Core.Scoops import Node as NodeScoop
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.BlenderUtil import get_object_accessor
from io_ggltf.Advanced import Settings, Attach
from io_ggltf.Core import Util, BlenderUtil
import bpy

#__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
__scoopCommand = lambda bucket, assignedID, objID, parent: NodeScoop.scoop_object(bucket=bucket, assignedID=assignedID, objAccessor=objID, parent=parent)

def based_on_object(bucket: Bucket, objAccessor, parent=None, checkRedundancies=None, name=None, autoLinkData=None, inSpace=None) -> int:

    obj = try_get_object(objAccessor)
    if parent == None:
        parent = Settings.get_setting(bucket, __k.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)

    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, __k.BUCKET_SETTING_REDUNDANCY_CHECK_NODE)
    if autoLinkData == None:
        autoLinkData = Settings.get_setting(bucket, __k.BUCKET_SETTING_NODE_AUTO_LINK_DATA)

    if checkRedundancies:
        redundant, nodeID = RM.register_unique(bucket, get_object_accessor(obj), __k.BUCKET_DATA_NODES, bpy.data.objects.get)
        if redundant:
            return nodeID
    else:
        nodeID = RM.register_unsafe(bucket, get_object_accessor(obj), __k.BUCKET_DATA_NODES)

    if name != None:
        if type(name) == str:
            bucket.commandQueue[__k.COMMAND_QUEUE_NAMING].append((Util.rename_node, (bucket, nodeID, name)))
        else:
            raise Exception(f"based_on_object: 'name' is expected to be a string, got {type(name)} instead.")

    if type(parent) != bool and type(parent) != int:
        parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
    if inSpace == None:
        inSpace = parent
        
    bucket.commandQueue[__k.COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), inSpace)))

    if autoLinkData:
        __add_mesh(bucket, obj)
        __add_skin(bucket, obj, filters=[Util.create_filter(".*", False)], blacklist={})

    __auto_parent(bucket, obj, nodeID, parent)

    return nodeID


def based_on_hierarchy(bucket: Bucket, topObjAccessor, blacklist = {}, parent=None, checkRedundancies=None, filters=[], autoLinkData=None, inSpace=None) -> int:
    def __recursive(bucket: Bucket, obj, blacklist, parent, checkRedundancies, filters, autoLinkData, inSpace):
        if obj.name in blacklist or not Util.name_passes_filters(filters, obj.name):
            return None

        childrenIDs = []
        if __object_is_collection_instance(obj):
            childrenIDs.extend(based_on_collection(bucket=bucket, collectionName=get_object_accessor(obj.instance_collection), blacklist=blacklist, parent=True, checkRedundancies=checkRedundancies))
        else:
            for c in obj.children:
                childID = __recursive(bucket, c, blacklist, True, checkRedundancies, filters, autoLinkData)
                if childID != None:
                    childrenIDs.append(childID)

        if checkRedundancies:
            redundant, nodeID = RM.register_unique(bucket, get_object_accessor(obj), __k.BUCKET_DATA_NODES, bpy.data.objects.get)
            if redundant:
                return nodeID
        else:
            nodeID = RM.register_unsafe(bucket, get_object_accessor(obj), __k.BUCKET_DATA_NODES)

        for c in childrenIDs:
            Attach.node_to_node(bucket, c, nodeID)
        
        if type(parent) != bool and type(parent) != int:
            parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
        if inSpace == None:
            inSpace = parent
        bucket.commandQueue[__k.COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), inSpace)))
        if autoLinkData:
            __add_mesh(bucket, obj)
            __add_skin(bucket, obj, blacklist, filters)
        return nodeID

    obj = try_get_object(topObjAccessor)

    if parent == None:
        parent = Settings.get_setting(bucket, __k.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, __k.BUCKET_SETTING_REDUNDANCY_CHECK_NODE)
    if autoLinkData == None:
        autoLinkData = Settings.get_setting(bucket, __k.BUCKET_SETTING_NODE_AUTO_LINK_DATA)

    if type(parent) != bool and type(parent) != int:
        parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
    if inSpace == None:
        inSpace = parent
    topNodeID = __recursive(bucket, obj, blacklist, parent, checkRedundancies, filters, autoLinkData, inSpace)

    __auto_parent(bucket, obj, topNodeID, parent)

    return topNodeID


def __object_is_collection_instance(obj) -> bool:
    return obj.instance_type == __k.BLENDER_INSTANCE_TYPE_COLLECTION

def __get_collection_top_objects(collection, blacklist={}):
    topObjects = []
    for obj in collection.objects:
        if obj.parent == None and not obj.name in blacklist:
            topObjects.append(obj)
    return topObjects

def based_on_collection(bucket: Bucket, collectionName, blacklist={}, parent=None, checkRedundancies=None, filters=[], autoLinkData=None, inSpace=None) -> list:
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, __k.BUCKET_SETTING_REDUNDANCY_CHECK_NODE)
    if parent == None:
        parent = Settings.get_setting(bucket, __k.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)
    if autoLinkData == None:
        autoLinkData = Settings.get_setting(bucket, __k.BUCKET_SETTING_NODE_AUTO_LINK_DATA)

    collection = bpy.data.collections.get(collectionName)

    topObjects = __get_collection_top_objects(collection)

    if type(parent) != bool and type(parent) != int:
        parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
    if inSpace == None:
        inSpace = parent

    nodeIDs = []
    for topObj in topObjects:
        if not topObj.name in blacklist and Util.name_passes_filters(filters, topObj.name):
            nodeIDs.append(based_on_hierarchy(bucket, get_object_accessor(topObj), blacklist, parent, checkRedundancies, filters=filters, inSpace=inSpace))

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
        Attach.node_to_node(bucket, childID, parent)
        return

    if type(parent) == tuple:
        parentID = __get_parent_id(bucket, parent)
        Attach.node_to_node(bucket, childID, parentID)
        return

    raise Exception(f"Failed to resolve parent for '{BlenderUtil.get_object_accessor(childObj)}', parent accessor was: '{parent}'. Make sure that parent is added before the child")

def __get_parent_id(bucket: Bucket, accessor):
    id = RM.fetch_unique(bucket, accessor)
    if id != None:
        return id

    id = RM.fetch_last_id_from_unsafe(bucket, accessor, __k.BUCKET_DATA_NODES)
    if id != None:
        return id

    raise Exception(f"{accessor} needs to be added before it's children can access it")

def __add_mesh(bucket, obj):
    if Settings.get_setting(bucket, __k.BUCKET_SETTING_INCLUDE_MESH):
        if BlenderUtil.object_is_meshlike(obj):
            from io_ggltf.Advanced import Mesh
            Mesh.based_on_object(bucket, BlenderUtil.get_object_accessor(obj), autoLink=True)

def __add_skin(bucket, obj, blacklist, filters):
    if Settings.get_setting(bucket, __k.BUCKET_SETTING_INCLUDE_SKIN):
        if BlenderUtil.object_is_armature(obj):
            from io_ggltf.Advanced import Skin
            Skin.based_on_object(bucket, BlenderUtil.get_object_accessor(obj), autoLink=True, attachmentBlacklist=blacklist, attachmentFilters=filters)

def dummy(bucket: Bucket, name: str):
    id = RM.register_dummy(bucket, __k.BUCKET_DATA_NODES)
    bucket.commandQueue[__k.COMMAND_QUEUE_NODE].append((NodeScoop.make_dummy, (bucket, id, name)))
    return id