from pprint import isreadable
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Scoops import Node as NodeScoop
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
from io_advanced_gltf2.Core import Linker
import bpy

__linkChildCommand = lambda bucket, pID, cID: Linker.node_to_node(bucket=bucket, parentID=pID, childID=cID)
__scoopCommand = lambda bucket, obj, space: NodeScoop.scoop_object(bucket=bucket, obj=obj, localSpace=space)

def add_based_on_object(bucket: Bucket, objName, worldSpace=False) -> int:
    obj = bpy.data.objects.get(objName)
    if obj == None:
        raise Exception(f"{objName} was not found within blend file data")


    redundant, nodeID = RM.smart_redundancy(bucket, obj, BUCKET_DATA_NODES)
    if redundant:
        return nodeID
    else:
        bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, obj, not worldSpace)))
        return nodeID

def add_based_on_hierarchy(bucket: Bucket, topObjName, blacklist = [], topObjWorldSpace=False) -> int:
    def __recursive(bucket: Bucket, cObj, blacklist, worldSpace):
        if cObj.name in blacklist:
            return None

        cIDs = []
        for c in obj.children:
            cID = __recursive(bucket, c, blacklist, False)
            if cID != None:
                cIDs.append

        redundant, nodeID = RM.smart_redundancy(bucket, c, BUCKET_DATA_NODES)
        if redundant:
            return nodeID
        else:
            for c in cIDs:
                bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__linkChildCommand, (bucket, nodeID, c)))
            bucket.commandQueue[COMMAND_QUEUE_NODE].append((__scoopCommand, (bucket, obj, not worldSpace)))

    obj = bpy.data.objects.get(topObjName)
    if obj == None:
        raise Exception(f"{topObjName} was not found within blend file data")

    return __recursive(bucket, obj, blacklist, topObjWorldSpace)
