from io_ggltf import Constants as __c
from io_ggltf.Core.Scoops import Node as NodeScoop
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.BlenderUtil import get_object_accessor
from io_ggltf.Advanced import Settings, Attach, Scene
from io_ggltf.Core import Util, BlenderUtil
import bpy
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI
from io_ggltf.Core.Validation import FilterValidation

#__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
__scoopCommand = lambda bucket, assignedID, objID, parent: NodeScoop.scoop(bucket=bucket, assignedID=assignedID, accessor=objID, parent=parent)

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Node-Module#based_on_object")
def based_on_object(bucket: Bucket, objAccessor, parent=None, checkRedundancies=None, name=None, autoAttachData=None, inSpace=None, sceneID=None) -> int:
    """Create a node based on the object transformations"""

    obj = try_get_object(objAccessor)
    if parent == None:
        parent = Settings.get_setting(bucket, __c.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)

    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, __c.BUCKET_SETTING_REDUNDANCY_CHECK_NODE)
    if autoAttachData == None:
        autoAttachData = Settings.get_setting(bucket, __c.BUCKET_SETTING_NODE_AUTO_ATTACH_DATA)

    if checkRedundancies:
        redundant, nodeID = RM.register_unique(bucket, get_object_accessor(obj), __c.BUCKET_DATA_NODES)
        if redundant:
            return nodeID
    else:
        nodeID = RM.register_unsafe(bucket, get_object_accessor(obj), __c.BUCKET_DATA_NODES)

    if name != None:
        if type(name) == str:
            bucket.commandQueue[__c.COMMAND_QUEUE_NAMING].append((Util.rename_node, (bucket, nodeID, name)))
        else:
            raise Exception(f"based_on_object: 'name' is expected to be a string, got {type(name)} instead.")

    if type(parent) != bool and type(parent) != int and type(parent) != tuple:
        parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
    if inSpace == None:
        inSpace = parent
        
    bucket.commandQueue[__c.COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), inSpace)))

    if autoAttachData:
        __add_mesh(bucket, obj)
        __add_skin(bucket, obj, filters=[Util.create_filter(".*", False)], blacklist={})

    __auto_parent(bucket, obj, nodeID, parent)

    if sceneID != None:
        Scene.append_node(bucket, sceneID, nodeID)

    return nodeID


@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Node-Module#based_on_hierarchy")
def based_on_hierarchy(bucket: Bucket, topObjAccessor, blacklist = {}, parent=None, checkRedundancies=None, filters=[], autoAttachData=None, inSpace=None, sceneID=None) -> int:
    """Create a node hierarcht based on the object and its children transformations"""

    def __recursive(bucket: Bucket, obj, blacklist, parent, checkRedundancies, filters, autoAttachData, inSpace):
        if obj.name in blacklist or not Util.name_passes_filters(filters, obj.name):
            return None

        childrenIDs = []
        if __object_is_collection_instance(obj):
            childrenIDs.extend(based_on_collection(bucket=bucket, collectionName=get_object_accessor(obj.instance_collection), blacklist=blacklist, parent=True, checkRedundancies=checkRedundancies))
        else:
            for c in obj.children:
                if obj.type == __c.BLENDER_TYPE_ARMATURE and c.parent_type == __c.BLENDER_TYPE_OBJECT: # ignore children that belong to the armature of the current object
                    childID = __recursive(bucket, c, blacklist, True, checkRedundancies, filters, autoAttachData, True)
                    if childID != None:
                        childrenIDs.append(childID)

        if checkRedundancies:
            redundant, nodeID = RM.register_unique(bucket, get_object_accessor(obj), __c.BUCKET_DATA_NODES)
            if redundant:
                return nodeID
        else:
            nodeID = RM.register_unsafe(bucket, get_object_accessor(obj), __c.BUCKET_DATA_NODES)

        for c in childrenIDs:
            Attach.node_to_node(bucket, c, nodeID)
        
        if type(parent) != bool and type(parent) != int and type(parent) != tuple:
            parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
        if inSpace == None:
            inSpace = parent
        bucket.commandQueue[__c.COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, get_object_accessor(obj), inSpace)))
        if autoAttachData:
            __add_mesh(bucket, obj)
            __add_skin(bucket, obj, blacklist, filters)
        return nodeID

    filters = FilterValidation.validate_filter_arg(filters)

    obj = try_get_object(topObjAccessor)

    if parent == None:
        parent = Settings.get_setting(bucket, __c.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)
    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, __c.BUCKET_SETTING_REDUNDANCY_CHECK_NODE)
    if autoAttachData == None:
        autoAttachData = Settings.get_setting(bucket, __c.BUCKET_SETTING_NODE_AUTO_ATTACH_DATA)

    if type(parent) != bool and type(parent) != int and type(parent) != tuple:
        parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
    if inSpace == None:
        inSpace = parent
    topNodeID = __recursive(bucket, obj, blacklist, parent, checkRedundancies, filters, autoAttachData, inSpace)

    __auto_parent(bucket, obj, topNodeID, parent)

    if sceneID != None:
        Scene.append_node(bucket, sceneID, topNodeID)

    return topNodeID


def __object_is_collection_instance(obj) -> bool:
    return obj.instance_type == __c.BLENDER_INSTANCE_TYPE_COLLECTION

def __get_collection_top_objects(collection, blacklist={}):
    topObjects = []
    for obj in collection.objects:
        if obj.parent == None and not obj.name in blacklist:
            topObjects.append(obj)
    return topObjects

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Node-Module#based_on_collection")
def based_on_collection(bucket: Bucket, collectionName, blacklist={}, parent=None, checkRedundancies=None, filters=[], autoAttachData=None, inSpace=None, sceneID=None) -> list:
    """Create node hierarchies based on all object found in collection"""

    filters = FilterValidation.validate_filter_arg(filters)

    if checkRedundancies == None:
        checkRedundancies = Settings.get_setting(bucket, __c.BUCKET_SETTING_REDUNDANCY_CHECK_NODE)
    if parent == None:
        parent = Settings.get_setting(bucket, __c.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE)
    if autoAttachData == None:
        autoAttachData = Settings.get_setting(bucket, __c.BUCKET_SETTING_NODE_AUTO_ATTACH_DATA)

    collection = bpy.data.collections.get(collectionName)

    topObjects = __get_collection_top_objects(collection)

    if type(parent) != bool and type(parent) != int and type(parent) != tuple:
        parent = BlenderUtil.get_object_accessor(Util.try_get_object(parent))
    if inSpace == None:
        inSpace = parent

    nodeIDs = []
    for topObj in topObjects:
        if not topObj.name in blacklist and Util.name_passes_filters(filters, topObj.name):
            nodeIDs.append(based_on_hierarchy(bucket, get_object_accessor(topObj), blacklist, parent, checkRedundancies, filters=filters, inSpace=inSpace))

    if sceneID != None:
        for n in nodeIDs:
            Scene.append_node(bucket, sceneID, n)

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
                parent = BlenderUtil.get_parent_accessor(BlenderUtil.get_object_accessor(childObj)) # this will trigger  == tuple below
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
    try:
        id = RM.fetch_unique(bucket, accessor)
        if id != None:
            return id
    except:
        pass

    id = RM.fetch_last_id_from_unsafe(bucket, accessor, __c.BUCKET_DATA_NODES)
    if id != None:
        return id

    raise Exception(f"{accessor} needs to be added before it's children can access it")

def __add_mesh(bucket, obj):
    if Settings.get_setting(bucket, __c.BUCKET_SETTING_INCLUDE_MESH):
        if BlenderUtil.object_is_meshlike(obj):
            from io_ggltf.Advanced import Mesh
            Mesh.based_on_object(bucket, BlenderUtil.get_object_accessor(obj), autoAttach=True)

def __add_skin(bucket, obj, blacklist, filters):
    if Settings.get_setting(bucket, __c.BUCKET_SETTING_INCLUDE_SKIN):
        if BlenderUtil.object_is_armature(obj):
            from io_ggltf.Advanced import Skin
            Skin.based_on_object(bucket, BlenderUtil.get_object_accessor(obj), autoLink=True, attachmentBlacklist=blacklist, attachmentFilters=filters)

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Node-Module#dummy")
def dummy(bucket: Bucket, name: str, sceneID = None):
    """Create a node that has no transformation"""

    id = RM.register_dummy(bucket, __c.BUCKET_DATA_NODES)
    bucket.commandQueue[__c.COMMAND_QUEUE_NODE].append((NodeScoop.make_dummy, (bucket, id, name)))

    if sceneID != None:
        Scene.append_node(bucket, sceneID, id)

    return id