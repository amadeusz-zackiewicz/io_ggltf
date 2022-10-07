from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.Scoops import Skin
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import BlenderUtil, Util
from io_ggltf.Advanced import Settings, Attach
import bpy

__setArmaturePoseCommand = lambda bucket, objAccessor, poseMode: BlenderUtil.set_object_pose_mode(bucket=bucket, objAccessor=objAccessor, poseMode=poseMode)
__scoopSkinCommand = lambda bucket, skinID, objAccessor, getInverse, boneBlackList, boneOffset, filters, rigify: Skin.scoop_skin(bucket=bucket, objAccessors=objAccessor,getInversedBinds=getInverse, blacklist=boneBlackList, nodeIDOffset=boneOffset, skinID=skinID, filters=filters, stitch=rigify) # TODO: need to provide bone node offsets and skin id

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
    autoLink = None
) -> int:
    
    if checkRedundancy == None:
        checkRedundancy = Settings.get_setting(bucket, __k.BUCKET_SETTING_REDUNDANCY_CHECK_SKIN)
    if getInverseBinds == None:
        getInverseBinds = Settings.get_setting(bucket, __k.BUCKET_SETTING_SKIN_GET_INVERSED_BINDS)
    if forceRestPose == None:
        forceRestPose = Settings.get_setting(bucket, __k.BUCKET_SETTING_SKIN_FORCE_REST_POSE)
    if rigifyFlags == None:
        rigifyFlags = Settings.get_setting(bucket, __k.BUCKET_SETTING_SKIN_RIGIFY_FLAGS)
    if autoLink == None:
        autoLink = Settings.get_setting(bucket, __k.BUCKET_SETTING_SKIN_AUTO_LINK)

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None

    accessor = BlenderUtil.get_object_accessor(obj)

    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, accessor, __k.BUCKET_DATA_SKINS)

        if redundant:
            return skinID
    else:
        skinID = RM.register_unsafe(bucket, accessor, __k.BUCKET_DATA_SKINS)
    
    if forceRestPose:
        if obj.data.pose_position != __k.BLENDER_ARMATURE_REST_MODE:
            BlenderUtil.queue_reset_armature_pose(bucket, obj)
            bucket.commandQueue[__k.COMMAND_QUEUE_SKIN].append((__setArmaturePoseCommand, (bucket, objAccessor, __k.BLENDER_ARMATURE_REST_MODE)))
            BlenderUtil.queue_update_depsgraph(bucket, __k.COMMAND_QUEUE_SKIN)

    rigify = __is_rigify(obj)
    if rigify:
        boneFilters.extend(BlenderUtil.create_rigify_filters(rigifyFlags))
    boneOffset, skinDefinition = Skin.get_skin_definition(bucket, [accessor], boneBlackList, boneFilters)
    bucket.skinDefinition.append(skinDefinition)
    bucket.commandQueue[__k.COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, [accessor], getInverseBinds, boneBlackList, boneOffset, boneFilters, rigify)))

    __link_bone_attachments(bucket, Skin.get_attachments([accessor], boneBlackList, boneFilters), attachmentBlacklist, attachmentFilters)

    if autoLink:
        Attach.skin_to_unsafe_node(bucket, skinID, accessor)

    return skinID


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
    autoLink = None
) -> int:

    if checkRedundancy == None:
        checkRedundancy = bucket.settings[__k.BUCKET_SETTING_REDUNDANCY_CHECK_SKIN]
    if getInverseBinds == None:
        getInverseBinds = bucket.settings[__k.BUCKET_SETTING_SKIN_GET_INVERSED_BINDS]
    if forceRestPose == None:
        forceRestPose = bucket.settings[__k.BUCKET_SETTING_SKIN_FORCE_REST_POSE]
    if autoLink == None:
        autoLink = Settings.get_setting(bucket, __k.BUCKET_SETTING_SKIN_AUTO_LINK)

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None

    armatureObjects = []
    depsGraph = bucket.currentDependencyGraph

    for mod in obj.modifiers:
        if mod.type == __k.BLENDER_MODIFIER_ARMATURE:
            if depsGraph.mode == __k.BLENDER_DEPSGRAPH_MODE_VIEWPORT and mod.show_viewport or depsGraph.mode == __k.BLENDER_DEPSGRAPH_MODE_RENDER and mod.show_render:
                armatureObjects.append(mod.object)

    if len(armatureObjects) == 0:
        print("No armature modifiers found")
        return None

    objectAccessors = [BlenderUtil.get_object_accessor(o) for o in armatureObjects]
    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, objectAccessors, __k.BUCKET_DATA_SKINS)

        if redundant:
            return skinID
    else:
        skinID = RM.register_unsafe(bucket, objectAccessors, __k.BUCKET_DATA_SKINS)

    rigify = False

    for armatureObj in armatureObjects:
        if forceRestPose:
            if armatureObj.data.pose_position != __k.BLENDER_ARMATURE_REST_MODE:
                BlenderUtil.queue_reset_armature_pose(bucket, armatureObj)
                bucket.commandQueue[__k.COMMAND_QUEUE_SKIN].append((__setArmaturePoseCommand, (bucket, BlenderUtil.get_object_accessor(armatureObj), __k.BLENDER_ARMATURE_REST_MODE)))
        
        if __is_rigify(armatureObj):
            rigify = True

    BlenderUtil.queue_update_depsgraph(bucket, __k.COMMAND_QUEUE_SKIN)
    if rigify:
        boneFilters.extend(BlenderUtil.create_rigify_filters(rigifyFlags))
    boneOffset, skinDefinition = Skin.get_skin_definition(bucket, objectAccessors, boneBlackList)
    bucket.skinDefinition.append(skinDefinition)
    bucket.commandQueue[__k.COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, objectAccessors, getInverseBinds, boneBlackList, boneOffset, boneFilters, rigify)))

    __link_bone_attachments(bucket, Skin.get_attachments(objectAccessors, boneBlacklist=boneBlackList, boneFilters=boneFilters, attachmentBlacklist=attachmentBlacklist, attachmentFilters=attachmentFilters))

    if autoLink:
        Attach.skin_to_unsafe_node(bucket, skinID, BlenderUtil.get_object_accessor(obj))

    return skinID


def __link_bone_attachments(bucket: Bucket, attachments, blacklist = set(), filters = []):
    from io_ggltf.Advanced import Node
    for attachment in attachments:
        Node.based_on_hierarchy(bucket, BlenderUtil.get_object_accessor(attachment), blacklist=blacklist, filters=filters, parent=BlenderUtil.get_parent_accessor(attachment))
        RM.fetch_last_id_from_unsafe(bucket, BlenderUtil.get_parent_accessor(attachment), __k.BUCKET_DATA_NODES)

def __is_rigify(armatureObj):
    return armatureObj.data.get("rig_id") != None