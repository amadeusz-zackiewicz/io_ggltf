from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Managers import RedundancyManager as RM
import bpy

def set_object_pose_mode(bucket: Bucket, objAccessor, poseMode):
    obj = bpy.data.objects.get(objAccessor)
    obj.data.pose_position = poseMode

def set_object_modifier(bucket: Bucket, objAccessor, modifierID, setActive):
    obj = bpy.data.objects.get(objAccessor)
    if bucket.currentDependencyGraph.mode == __k.BLENDER_DEPSGRAPH_MODE_VIEWPORT:
        obj.modifiers[modifierID].show_viewport = setActive
    else:
        obj.modifiers[modifierID].show_render = setActive

def get_object_accessor(obj):
    return (obj.name, obj.library.filepath if obj.library != None else None)

def get_bone_accessor(armatureObj, bone):
    return (armatureObj.name, armatureObj.library.filepath if armatureObj.library != None else None, bone)

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
            bucket.commandQueue[__k.COMMAND_QUEUE_SETUP].append((__disable_modifier_command,(bucket, get_object_accessor(obj), i)))
            bucket.commandQueue[__k.COMMAND_QUEUE_CLEAN_UP].append((__enable_modifier_command, (bucket, get_object_accessor(obj), i)))

def create_rigify_filters(rigifyFlags):
    if rigifyFlags & ~__k.RIGIFY_TRIM_NAMES != 0: # clear the RIGIFY_TRIM_NAMES flag
        filters = []
        rootFilter = None
        if rigifyFlags & __k.RIGIFY_INCLUDE_CONTROLS == __k.RIGIFY_INCLUDE_CONTROLS:
            whitelist = False
            if rigifyFlags & __k.RIGIFY_INCLUDE_ORIGINAL == 0:
                filters.append("(^ORG-)")
            if rigifyFlags & __k.RIGIFY_INCLUDE_DEFORMS == 0:
                filters.append("(^DEF-)")
        else:
            whitelist = True
            if rigifyFlags & __k.RIGIFY_INCLUDE_ORIGINAL == __k.RIGIFY_INCLUDE_ORIGINAL:
                filters.append("(^ORG-)")
            if rigifyFlags & __k.RIGIFY_INCLUDE_DEFORMS == __k.RIGIFY_INCLUDE_DEFORMS:
                filters.append("(^DEF-)")
            if rigifyFlags & __k.RIGIFY_INCLUDE_ROOT:
                rootFilter = "(^root$)"
        if len(filters) > 0:
            if rootFilter != None:
                filters.extend([rootFilter])
            return [("|".join(filters), whitelist)]
        else:
            if rootFilter != None:
                return [rootFilter]
    return []

def rigify_rename(bucket, rigifyFlags):
    if rigifyFlags & __k.RIGIFY_TRIM_NAMES == 0 or rigifyFlags & __k.RIGIFY_INCLUDE_CONTROLS != 0:
        print("Trimming rigify names was omitted as there would be multiple duplicate nodes with identical hierarchies (RIGIFY_INCLUDE_CONTROLS | RIGIFY_TRIM_NAMES)")
        return None # if controls are included then we ignore the name trimming since that will produce a lot of duplicates
    if rigifyFlags & __k.RIGIFY_INCLUDE_DEFORMS == __k.RIGIFY_INCLUDE_DEFORMS and rigifyFlags & __k.RIGIFY_INCLUDE_ORIGINAL == __k.RIGIFY_INCLUDE_ORIGINAL:
        print("Trimming rigify names was omitted as there would be multiple duplicate nodes with identical hierarchies (RIGIFY_INCLUDE_DEFORMS | RIGIFY_INCLUDE_ORIGINAL | RIGIFY_TRIM_NAMES")
        return None # if both original and deforms are included then we will have duplicate names

    if rigifyFlags & __k.RIGIFY_INCLUDE_ORIGINAL:
        return "^ORG-"
    if rigifyFlags & __k.RIGIFY_INCLUDE_DEFORMS:
        return "^DEF-"

    return None

def get_parent_accessor(obj):
    if obj.parent != None:
        if obj.parent_type == __k.BLENDER_TYPE_BONE:
            return get_bone_accessor(obj.parent, obj.parent_bone)
        else:
            return get_object_accessor(obj.parent)
    else:
        return None

