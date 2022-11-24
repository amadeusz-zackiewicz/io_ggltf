from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import Util
import bpy
import re

def set_object_pose_mode(bucket: Bucket, objAccessor, poseMode):
    obj = bpy.data.objects.get(objAccessor)
    obj.data.pose_position = poseMode

def set_object_modifier(bucket: Bucket, objAccessor, modifierID, setActive):
    obj = bpy.data.objects.get(objAccessor)
    if bucket.currentDependencyGraph.mode == __c.BLENDER_DEPSGRAPH_MODE_VIEWPORT:
        obj.modifiers[modifierID].show_viewport = setActive
    else:
        obj.modifiers[modifierID].show_render = setActive

def get_object_accessor(obj):
    return (obj.name, obj.library.filepath if obj.library != None else None)

def get_bone_accessor(armatureObj, bone):
    return (armatureObj.name, armatureObj.library.filepath if armatureObj.library != None else None, bone)

__disable_modifier_command = lambda bucket, objAccessor, modifierID: set_object_modifier(bucket=bucket, objAccessor=objAccessor, modifierID=modifierID, setActive=False)
__enable_modifier_command = lambda bucket, objAccessor, modifierID: set_object_modifier(bucket=bucket, objAccessor=objAccessor, modifierID=modifierID, setActive=True)

def queue_disable_modifier_type(bucket, obj, modType, queue):
    for i, mod in enumerate(obj.modifiers):
        if mod.type == modType:
            if mod.show_viewport:
                bucket.commandQueue[queue].append((__disable_modifier_command,(bucket, get_object_accessor(obj), i)))


def queue_reset_modifier_changes(bucket, obj, modType):
    for i, mod in enumerate(obj.modifiers):
        if mod.type == modType:
            if mod.show_viewport:
                bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((__enable_modifier_command, (bucket, get_object_accessor(obj), i)))
            else:
                bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((__disable_modifier_command, (bucket, get_object_accessor(obj), i)))

def queue_update_depsgraph(bucket: Bucket, queue):
    bucket.commandQueue[queue].append((bucket.currentDependencyGraph.update, ()))

def queue_reset_armature_pose(bucket: Bucket, obj):
    bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((set_object_pose_mode, (bucket, get_object_accessor(obj), obj.data.pose_position)))
    

def create_rigify_filters(rigifyFlags):
    if rigifyFlags & ~__c.RIGIFY_TRIM_NAMES != 0: # clear the RIGIFY_TRIM_NAMES flag
        filters = []
        extraFilters = []
        rootFilter = None
        if rigifyFlags & __c.RIGIFY_INCLUDE_CONTROLS == __c.RIGIFY_INCLUDE_CONTROLS:
            whitelist = False
            if rigifyFlags & __c.RIGIFY_INCLUDE_ORIGINAL == 0:
                filters.append("(^ORG-)")
            if rigifyFlags & __c.RIGIFY_INCLUDE_DEFORMS == 0:
                filters.append("(^DEF-)")
        else:
            whitelist = True
            if rigifyFlags & __c.RIGIFY_INCLUDE_ORIGINAL == __c.RIGIFY_INCLUDE_ORIGINAL:
                filters.append("(^ORG-)")
            if rigifyFlags & __c.RIGIFY_INCLUDE_DEFORMS == __c.RIGIFY_INCLUDE_DEFORMS:
                filters.append("(^DEF-)")
                extraFilters.append(("(^DEF-eye_master.*)", False))
            if rigifyFlags & __c.RIGIFY_INCLUDE_ROOT:
                rootFilter = "(^root$)"
        if len(filters) > 0:
            if rootFilter != None:
                filters.extend([rootFilter])
            filters = [("|".join(filters), whitelist)]
            filters.extend(extraFilters)
            return filters
        else:
            if rootFilter != None:
                return [rootFilter]
    return []

def rigify_rename(bucket, rigifyFlags):
    if rigifyFlags & __c.RIGIFY_TRIM_NAMES == 0 or rigifyFlags & __c.RIGIFY_INCLUDE_CONTROLS != 0:
        print("Trimming rigify names was omitted as there would be multiple duplicate nodes with identical hierarchies (RIGIFY_INCLUDE_CONTROLS | RIGIFY_TRIM_NAMES)")
        return None # if controls are included then we ignore the name trimming since that will produce a lot of duplicates
    if rigifyFlags & __c.RIGIFY_INCLUDE_DEFORMS == __c.RIGIFY_INCLUDE_DEFORMS and rigifyFlags & __c.RIGIFY_INCLUDE_ORIGINAL == __c.RIGIFY_INCLUDE_ORIGINAL:
        print("Trimming rigify names was omitted as there would be multiple duplicate nodes with identical hierarchies (RIGIFY_INCLUDE_DEFORMS | RIGIFY_INCLUDE_ORIGINAL | RIGIFY_TRIM_NAMES")
        return None # if both original and deforms are included then we will have duplicate names

    if rigifyFlags & __c.RIGIFY_INCLUDE_ORIGINAL:
        return "^ORG-"
    if rigifyFlags & __c.RIGIFY_INCLUDE_DEFORMS:
        return "^DEF-"

    return None

def get_parent_accessor(accessor: tuple):
    bone = Util.try_get_bone(accessor)
    obj = Util.try_get_object(accessor)
    if bone != None:
        if bone.parent != None:
            return (accessor[0], accessor[1], bone.parent.name)
    else:
        if obj.parent != None:
            if obj.parent_type == __c.BLENDER_TYPE_BONE:
                return get_bone_accessor(obj.parent, obj.parent_bone)
            else:
                return get_object_accessor(obj.parent)
        else:
            return None

def rigify_get_potential_parent_name(childName: str) -> str or None:
    match = re.search(r"\.[0-9]*$", childName)
    
    if match == None:
        return None
    
    matchStr = match.group(0)
    number = int(matchStr.replace(".", ""))

    if number == 0:
        return childName.replace(matchStr, "") # I believe this cannot happen, but just in case
    else:
        parentNumber = number - 1
        if parentNumber == 0:
            return childName.replace(matchStr, "")
        if parentNumber < 0:
            return None
        newStr = str(parentNumber)

        if len(newStr) < 3:
            newStr = "." + ("0" * (3 - len(newStr))) + newStr

        parentName = childName.replace(matchStr, newStr)
        return parentName

def object_is_meshlike(obj):
    return obj.type == __c.BLENDER_TYPE_MESH
    #return obj.type in __c.BLENDER_MESH_CONVERTIBLE

def object_is_armature(obj):
    return obj.type == __c.BLENDER_TYPE_ARMATURE

def get_active_uv_map_name(obj):
    if obj.type == __c.BLENDER_TYPE_MESH:
        active = obj.data.uv_layers.active
        if active == None:
            return []
        return [active.name]
    return []

def get_active_vertex_color_name(obj):
    if obj.type == __c.BLENDER_TYPE_MESH:
        active = obj.data.vertex_colors.active
        if active == None:
            return []
        return [active.name]
    return []

def get_active_shape_key_names(obj):
    sk = []
    if obj.type == __c.BLENDER_TYPE_MESH:
        for key in obj.data.shape_keys.key_blocks[1:]:
            if not key.mute:
                sk.append(key.name)
    return sk
