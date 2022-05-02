from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops import Skin
from io_advanced_gltf2.Simple import Node
from io_advanced_gltf2.Simple.File import get_current_bucket
import bpy

def add_based_on_object(objName, getInverseBinds = False, forceRestPose = False, boneBlacklist = []):

    bucket = get_current_bucket()
    oldPose = BLENDER_ARMATURE_POSE_MODE

    obj = bpy.data.objects.get(objName)
    if obj == None:
        print("obj not found")
        return None

    if forceRestPose:
        oldPose = obj.data.pose_position
        obj.data.pose_position = BLENDER_ARMATURE_REST_MODE
        bucket.currentDependencyGraph.update()
        obj = bpy.data.objects.get(objName) # we get the object again just in case reference is lost

    nodeID = Node.add_based_on_object((obj.name, obj.library), False)
    skinID, rootNodes = Skin.scoop_skin(bucket, obj, blacklist=boneBlacklist, getInversedBinds=getInverseBinds)

    nodeDict = get_current_bucket().data[BUCKET_DATA_NODES][nodeID]
    
    if NODE_CHILDREN in nodeDict:
        nodeDict[NODE_CHILDREN].extend(rootNodes)
    else:
        nodeDict[NODE_CHILDREN] = rootNodes

    if oldPose != obj.data.pose_position:
        obj.data.pose_position = oldPose
        bucket.currentDependencyGraph.update()

    return skinID

def append_to_node(nodeID, skinID):
    node = get_current_bucket().data[BUCKET_DATA_NODES][nodeID]
    node[NODE_SKIN] = skinID