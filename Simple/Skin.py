from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops import Skin
from io_advanced_gltf2.Simple.File import get_current_bucket
import bpy

def add_based_on_object(objName, forceRestPose = False, boneBlacklist = []):

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

    skinID = Skin.scoop_skin(bucket, obj, blacklist=boneBlacklist)

    if oldPose != obj.data.pose_position:
        obj.data.pose_position = oldPose
        bucket.currentDependencyGraph.update()

    return skinID

def append_to_node(nodeID, skinID):
    node = get_current_bucket().data[BUCKET_DATA_NODES][nodeID]
    node[NODE_SKIN] = skinID