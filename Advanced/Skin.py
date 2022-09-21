from io_ggltf.Keywords import *
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.Scoops import Skin
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import BlenderUtil, Util
from io_ggltf.Advanced import Settings
import bpy

__setArmaturePoseCommand = lambda bucket, objAccessor, poseMode: BlenderUtil.set_object_pose_mode(bucket=bucket, objAccessor=objAccessor, poseMode=poseMode)
__scoopSkinCommand = lambda bucket, skinID, objAccessor, getInverse, boneBlackList, boneOffset, filters: Skin.scoop_skin(bucket=bucket, objAccessors=objAccessor,getInversedBinds=getInverse, blacklist=boneBlackList, nodeIDOffset=boneOffset, skinID=skinID, filters=filters) # TODO: need to provide bone node offsets and skin id

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
    rigifyFlags = None
) -> int:
    
    if checkRedundancy == None:
        checkRedundancy = Settings.get_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_SKIN)
    if getInverseBinds == None:
        getInverseBinds = Settings.get_setting(bucket, BUCKET_SETTING_SKIN_GET_INVERSED_BINDS)
    if forceRestPose == None:
        forceRestPose = Settings.get_setting(bucket, BUCKET_SETTING_SKIN_FORCE_REST_POSE)
    if rigifyFlags == None:
        rigifyFlags = Settings.get_setting(bucket, BUCKET_SETTING_SKIN_RIGIFY_FLAGS)

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None

    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, BlenderUtil.get_object_accessor(obj), BUCKET_DATA_SKINS)

        if redundant:
            return skinID
    else:
        skinID = RM.register_unsafe(bucket, BlenderUtil.get_object_accessor(obj), BUCKET_DATA_SKINS)
    
    if forceRestPose:
        if obj.data.pose_position != BLENDER_ARMATURE_REST_MODE:
            bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__setArmaturePoseCommand, (bucket, objAccessor, BLENDER_ARMATURE_REST_MODE)))
            bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__setArmaturePoseCommand, (bucket, objAccessor, BLENDER_ARMATURE_POSE_MODE)))

    boneFilters.extend(BlenderUtil.create_rigify_filters(rigifyFlags))
    boneOffset, skinDefinition = Skin.get_skin_definition(bucket, [BlenderUtil.get_object_accessor(obj)], boneBlackList, boneFilters)
    bucket.skinDefinition.append(skinDefinition)
    bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, [BlenderUtil.get_object_accessor(obj)], getInverseBinds, boneBlackList, boneOffset, boneFilters)))

    __link_bone_attachments(bucket, Skin.get_attachments([BlenderUtil.get_object_accessor(obj)], boneBlackList, boneFilters), attachmentBlacklist, attachmentFilters)

    return skinID


def based_on_object_modifiers(
    bucket: Bucket,
    objAccessor,
    getInverseBinds=None,
    forceRestPose=None,
    checkRedundancy=None,
    boneBlackList={},
    boneFilters=[]
) -> int:

    if checkRedundancy == None:
        checkRedundancy = bucket.settings[BUCKET_SETTING_REDUNDANCY_CHECK_SKIN]
    if getInverseBinds == None:
        getInverseBinds = bucket.settings[BUCKET_SETTING_SKIN_GET_INVERSED_BINDS]
    if forceRestPose == None:
        forceRestPose = bucket.settings[BUCKET_SETTING_SKIN_FORCE_REST_POSE]

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None

    armatureObjects = []
    depsGraph = bucket.currentDependencyGraph

    for mod in obj.modifiers:
        if mod.type == BLENDER_MODIFIER_ARMATURE:
            if depsGraph.mode == BLENDER_DEPSGRAPH_MODE_VIEWPORT and mod.show_viewport or depsGraph.mode == BLENDER_DEPSGRAPH_MODE_RENDER and mod.show_render:
                armatureObjects.append(mod.object)

    if len(armatureObjects) == 0:
        print("No armature modifiers found")
        return None

    objectAccessors = [(o.name, o.library) for o in armatureObjects]
    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, objectAccessors, BUCKET_DATA_SKINS)

        if redundant:
            return skinID
    else:
        skinID = RM.register_unsafe(bucket, BlenderUtil.get_object_accessor(obj), BUCKET_DATA_SKINS)

    for armatureObj in armatureObjects:
        if forceRestPose:
            if armatureObj.data.pose_position != BLENDER_ARMATURE_REST_MODE:
                bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__setArmaturePoseCommand, (bucket, (armatureObj.name, armatureObj.library), BLENDER_ARMATURE_REST_MODE)))
                bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__setArmaturePoseCommand, (bucket, (armatureObj.name, armatureObj.library), BLENDER_ARMATURE_POSE_MODE)))

    boneOffset, skinDefinition = Skin.get_skin_definition(bucket, objectAccessors, boneBlackList)
    bucket.skinDefinition.append(skinDefinition)
    bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, objectAccessors, getInverseBinds, boneBlackList, boneOffset, boneFilters)))

    return skinID


def __link_bone_attachments(bucket: Bucket, attachments, blacklist = set(), filters = []):
    from io_ggltf.Advanced import Node, Linker
    for attachment in attachments:
        attachID = Node.based_on_hierarchy(bucket, BlenderUtil.get_object_accessor(attachment), blacklist=blacklist, filters=filters, parent=BlenderUtil.get_parent_accessor(attachment))
        boneID = RM.fetch_last_id_from_unsafe(bucket, BlenderUtil.get_parent_accessor(attachment), BUCKET_DATA_NODES)
        Linker.node_to_node(bucket, attachID, boneID)