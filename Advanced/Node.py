from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Scoops import Node as NodeScoop
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Util import try_get_object
from io_advanced_gltf2.Core import Linker
import bpy

__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
__scoopCommand = lambda bucket, assignedID, objID, space: NodeScoop.scoop_object(bucket=bucket, assignedID=assignedID, objID=objID, worldSpace=space)

def based_on_object(bucket: Bucket, objName, worldSpace=False) -> int:

    obj = try_get_object(objName)
    redundant, nodeID = RM.smart_redundancy(bucket, obj, BUCKET_DATA_NODES)
    if redundant:
        return nodeID
    else:
        bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, (obj.name, obj.library), worldSpace)))
        return nodeID

def based_on_hierarchy(bucket: Bucket, topObjName, blacklist = [], topObjWorldSpace=False) -> int:
    def __recursive(bucket: Bucket, obj, blacklist, worldSpace):
        if obj.name in blacklist:
            return None

        childrenIDs = []
        for c in obj.children:
            childID = __recursive(bucket, c, blacklist, False)
            if childID != None:
                childrenIDs.append(childID)

        redundant, nodeID = RM.smart_redundancy(bucket, obj, BUCKET_DATA_NODES)
        if redundant:
            return nodeID

        for c in childrenIDs:
            bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__linkChildCommand, (bucket, nodeID, c)))
        
        bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, nodeID, (obj.name, obj.library), worldSpace)))
        return nodeID

    obj = try_get_object(topObjName)

    return __recursive(bucket, obj, blacklist, topObjWorldSpace)
