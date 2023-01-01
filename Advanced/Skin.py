from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.Scoops import Skin
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import BlenderUtil, Util
from io_ggltf.Advanced import Settings, Attach
import bpy
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI
from io_ggltf.Core.Validation import FilterValidation

__setArmaturePoseCommand = lambda bucket, objAccessor, poseMode: BlenderUtil.set_object_pose_mode(bucket=bucket, objAccessor=objAccessor, poseMode=poseMode)
__scoopSkinCommand = lambda bucket, skinID, objAccessor, getInverse, boneBlackList, boneOffset, filters, rigify: Skin.scoop_skin(bucket=bucket, objAccessors=objAccessor,getInversedBinds=getInverse, blacklist=boneBlackList, nodeIDOffset=boneOffset, skinID=skinID, filters=filters, stitch=rigify) # TODO: need to provide bone node offsets and skin id

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Skin-Module#based_on_object")
def based_on_object(
    bucket: Bucket, 
    objAccessor,
    getInverseBinds=None,
    forceRestPose=None,
    checkRedundancy=None,
    boneBlackList={},
    boneFilters=[],
    attachmentBlacklist={},
    attachmentFilters=[],
    rigifyFlags = None,
    autoAttach = None
) -> int:
    """Create a skin based on armature object"""
    
    boneFilters = FilterValidation.validate_filter_arg(boneFilters)
    attachmentFilters = FilterValidation.validate_filter_arg(attachmentFilters)

    if checkRedundancy == None:
        checkRedundancy = Settings.get_setting(bucket, __c.BUCKET_SETTING_REDUNDANCY_CHECK_SKIN)
    if getInverseBinds == None:
        getInverseBinds = Settings.get_setting(bucket, __c.BUCKET_SETTING_SKIN_GET_INVERSED_BINDS)
    if forceRestPose == None:
        forceRestPose = Settings.get_setting(bucket, __c.BUCKET_SETTING_SKIN_FORCE_REST_POSE)
    if rigifyFlags == None:
        rigifyFlags = Settings.get_setting(bucket, __c.BUCKET_SETTING_SKIN_RIGIFY_FLAGS)
    if autoAttach == None:
        autoAttach = Settings.get_setting(bucket, __c.BUCKET_SETTING_SKIN_AUTO_ATTACH)

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None

    accessor = BlenderUtil.get_object_accessor(obj)

    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, accessor, __c.BUCKET_DATA_SKINS)

        if redundant:
            return skinID, []
    else:
        skinID = RM.register_unsafe(bucket, accessor, __c.BUCKET_DATA_SKINS)
    
    if forceRestPose:
        if obj.data.pose_position != __c.BLENDER_ARMATURE_REST_MODE:
            BlenderUtil.queue_reset_armature_pose(bucket, obj)
            bucket.commandQueue[__c.COMMAND_QUEUE_SKIN].append((__setArmaturePoseCommand, (bucket, objAccessor, __c.BLENDER_ARMATURE_REST_MODE)))
            BlenderUtil.queue_update_depsgraph(bucket, __c.COMMAND_QUEUE_SKIN)

    rigify = __is_rigify(obj)
    if rigify:
        boneFilters.extend(BlenderUtil.create_rigify_filters(rigifyFlags))
        __queue_trim_names(bucket, skinID, rigifyFlags)
    boneOffset, skinDefinition = Skin.get_skin_definition(bucket, [accessor], boneBlackList, boneFilters)
    bucket.skinDefinition.append(skinDefinition)
    bucket.commandQueue[__c.COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, [accessor], getInverseBinds, boneBlackList, boneOffset, boneFilters, rigify)))

    attachments = __link_bone_attachments(bucket, Skin.get_attachments([accessor], boneBlackList, boneFilters), attachmentBlacklist, attachmentFilters)

    if autoAttach:
        Attach.skin_to_unsafe_node(bucket, skinID, accessor)

    return skinID, attachments


def based_on_object_modifiers(
    bucket: Bucket, 
    objAccessor,
    getInverseBinds=None,
    forceRestPose=None,
    checkRedundancy=None,
    boneBlackList={},
    boneFilters=[],
    attachmentBlacklist={},
    attachmentFilters=[],
    rigifyFlags = None,
    autoAttach = None
) -> int:

    boneFilters = FilterValidation.validate_filter_arg(boneFilters)
    attachmentFilters = FilterValidation.validate_filter_arg(attachmentFilters)

    if checkRedundancy == None:
        checkRedundancy = bucket.settings[__c.BUCKET_SETTING_REDUNDANCY_CHECK_SKIN]
    if getInverseBinds == None:
        getInverseBinds = bucket.settings[__c.BUCKET_SETTING_SKIN_GET_INVERSED_BINDS]
    if forceRestPose == None:
        forceRestPose = bucket.settings[__c.BUCKET_SETTING_SKIN_FORCE_REST_POSE]
    if autoAttach == None:
        autoAttach = Settings.get_setting(bucket, __c.BUCKET_SETTING_SKIN_AUTO_ATTACH)

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None

    armatureObjects = []
    depsGraph = bucket.currentDependencyGraph

    for mod in obj.modifiers:
        if mod.type == __c.BLENDER_MODIFIER_ARMATURE:
            if depsGraph.mode == __c.BLENDER_DEPSGRAPH_MODE_VIEWPORT and mod.show_viewport or depsGraph.mode == __c.BLENDER_DEPSGRAPH_MODE_RENDER and mod.show_render:
                armatureObjects.append(mod.object)

    if len(armatureObjects) == 0:
        print("No armature modifiers found")
        return None

    objectAccessors = [BlenderUtil.get_object_accessor(o) for o in armatureObjects]
    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, objectAccessors, __c.BUCKET_DATA_SKINS)

        if redundant:
            return skinID, []
    else:
        skinID = RM.register_unsafe(bucket, objectAccessors, __c.BUCKET_DATA_SKINS)

    rigify = False

    for armatureObj in armatureObjects:
        if forceRestPose:
            if armatureObj.data.pose_position != __c.BLENDER_ARMATURE_REST_MODE:
                BlenderUtil.queue_reset_armature_pose(bucket, armatureObj)
                bucket.commandQueue[__c.COMMAND_QUEUE_SKIN].append((__setArmaturePoseCommand, (bucket, BlenderUtil.get_object_accessor(armatureObj), __c.BLENDER_ARMATURE_REST_MODE)))
        
        if __is_rigify(armatureObj):
            rigify = True

    BlenderUtil.queue_update_depsgraph(bucket, __c.COMMAND_QUEUE_SKIN)
    if rigify:
        boneFilters.extend(BlenderUtil.create_rigify_filters(rigifyFlags))
        __queue_trim_names(bucket, skinID, rigifyFlags)
    boneOffset, skinDefinition = Skin.get_skin_definition(bucket, objectAccessors, boneBlackList)
    bucket.skinDefinition.append(skinDefinition)
    bucket.commandQueue[__c.COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, objectAccessors, getInverseBinds, boneBlackList, boneOffset, boneFilters, rigify)))

    attachments = __link_bone_attachments(bucket, Skin.get_attachments(objectAccessors, boneBlacklist=boneBlackList, boneFilters=boneFilters, attachmentBlacklist=attachmentBlacklist, attachmentFilters=attachmentFilters))

    if autoAttach:
        Attach.skin_to_unsafe_node(bucket, skinID, BlenderUtil.get_object_accessor(obj))

    return skinID, attachments


def __link_bone_attachments(bucket: Bucket, attachments, blacklist = set(), filters = []):
    from io_ggltf.Advanced import Node
    attachIDs = []
    for attachment in attachments:
        attachmentAccessor = BlenderUtil.get_object_accessor(attachment)
        parentAccessor = BlenderUtil.get_parent_accessor(attachmentAccessor)
        attachmentID = Node.based_on_hierarchy(bucket, attachmentAccessor, blacklist=blacklist, filters=filters, parent=parentAccessor)
        attachIDs.append(attachIDs)

    return attachIDs

def __is_rigify(armatureObj):
    return armatureObj.data.get("rig_id") != None

def __queue_trim_names(bucket, skinID, rigifyFlags):
    if rigifyFlags & __c.RIGIFY_TRIM_NAMES == __c.RIGIFY_TRIM_NAMES:
            if rigifyFlags & __c.RIGIFY_INCLUDE_CONTROLS == __c.RIGIFY_INCLUDE_CONTROLS:
                return
            if rigifyFlags & (__c.RIGIFY_INCLUDE_DEFORMS | __c.RIGIFY_INCLUDE_ORIGINAL) == (__c.RIGIFY_INCLUDE_DEFORMS | __c.RIGIFY_INCLUDE_ORIGINAL):
                return
            
            if rigifyFlags & __c.RIGIFY_INCLUDE_DEFORMS == __c.RIGIFY_INCLUDE_DEFORMS:
                pattern = "^DEF-"
            elif rigifyFlags & __c.RIGIFY_INCLUDE_ORIGINAL == __c.RIGIFY_INCLUDE_ORIGINAL:
                pattern = "^ORG-"
            else:
                return

            bucket.commandQueue[__c.COMMAND_QUEUE_NAMING].append((Util.pattern_replace_skin_joint_names, (bucket, skinID, pattern, "")))