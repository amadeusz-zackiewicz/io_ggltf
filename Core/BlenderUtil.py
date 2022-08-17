from io_ggltf.Keywords import *
from io_ggltf.Core.Bucket import Bucket
import bpy

def set_object_pose_mode(bucket: Bucket, objAccessor, poseMode):
    obj = bpy.data.objects.get(objAccessor)
    obj.data.pose_position = poseMode

def set_object_modifier(bucket: Bucket, objAccessor, modifierID, setActive):
    obj = bpy.data.objects.get(objAccessor)
    if bucket.currentDependencyGraph.mode == BLENDER_DEPSGRAPH_MODE_VIEWPORT:
        obj.modifiers[modifierID].show_viewport = setActive
    else:
        obj.modifiers[modifierID].show_render = setActive

def get_object_accessor(obj):
    return (obj.name, obj.library.filepath if obj.library != None else None)

def object_has_uv_maps(obj, uvMaps: list[str]) -> bool:
    for map in uvMaps:
        if not map in obj.data.uv_layers:
            return False
    # all maps names were found
    return True

def object_has_vertex_colors(obj, vertexColors: list[str]) -> bool:
    for vc in vertexColors:
        if not vc in obj.data.vertex_colors:
            return False
    # all vertex colors names found
    return True

def object_has_shape_keys(obj, shapeKeys: list[str]) -> bool:
    for key in shapeKeys:
        if key not in obj.data.shape_keys.key_blocks:
            return False
    # all shape keys found
    return True

__disable_modifier_command = lambda bucket, objAccessor, modifierID: set_object_modifier(bucket=bucket, objAccessor=objAccessor, modifierID=modifierID, setActive=False)
__enable_modifier_command = lambda bucket, objAccessor, modifierID: set_object_modifier(bucket=bucket, objAccessor=objAccessor, modifierID=modifierID, setActive=True)

def queue_disable_modifier_type(bucket, obj, modType):
    for i, mod in enumerate(obj.modifiers):
        if mod.type == modType:
            bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__disable_modifier_command,(bucket, get_object_accessor(obj), i)))
            bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__enable_modifier_command, (bucket, get_object_accessor(obj), i)))