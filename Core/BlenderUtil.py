from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
import bpy

def set_object_pose_mode(bucket: Bucket, objName, poseMode):
    obj = bpy.data.objects.get(objName)
    obj.data.pose_position = poseMode

def set_object_modifier(bucket: Bucket, objName, modifierID, setActive):
    obj = bpy.data.objects.get(objName)
    if bucket.currentDependencyGraph.mode == BLENDER_DEPSGRAPH_MODE_VIEWPORT:
        obj.modifiers[modifierID].show_viewport = setActive
    else:
        obj.modifiers[modifierID].show_render = setActive
