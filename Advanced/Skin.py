from io_ggltf.Keywords import *
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.Scoops import Skin
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import BlenderUtil
import bpy

__setArmaturePoseCommand = lambda bucket, objAccessor, poseMode: BlenderUtil.set_object_pose_mode(bucket=bucket, objAccessor=objAccessor, poseMode=poseMode)
__scoopSkinCommand = lambda bucket, skinID, objAccessor, getInverse, boneBlackList, boneOffset: Skin.scoop_skin(bucket=bucket, objAccessors=objAccessor,getInversedBinds=getInverse, blacklist=boneBlackList, nodeIDOffset=boneOffset, skinID=skinID) # TODO: need to provide bone node offsets and skin id

def based_on_object(
    bucket: Bucket, 
    objAccessor,
    getInverseBinds=None,
    forceRestPose=None,
    checkRedundancy=None,
    boneBlackList=[]
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

    if checkRedundancy:
        redundant, skinID = RM.register_unique(bucket, (obj.name, obj.library), BUCKET_DATA_SKINS)

        if redundant:
            return skinID
    else:
        skinID = RM.register_unsafe(bucket, BlenderUtil.get_object_accessor(obj), BUCKET_DATA_SKINS)
    
    if forceRestPose:
        if obj.data.pose_position != BLENDER_ARMATURE_REST_MODE:
            bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__setArmaturePoseCommand, (bucket, objAccessor, BLENDER_ARMATURE_REST_MODE)))
            bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__setArmaturePoseCommand, (bucket, objAccessor, BLENDER_ARMATURE_POSE_MODE)))

    boneOffset = Skin.reserve_bone_ids(bucket, [(obj.name, obj.library)], boneBlackList) 
    bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, [(obj.name, obj.library)], getInverseBinds, boneBlackList, boneOffset)))
    return skinID


def based_on_object_modifiers(
    bucket: Bucket,
    objAccessor,
    getInverseBinds=None,
    forceRestPose=None,
    checkRedundancy=None,
    boneBlackList=[]
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

    boneOffset = Skin.reserve_bone_ids(bucket, objectAccessors, boneBlackList) 
    bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, objectAccessors, getInverseBinds, boneBlackList, boneOffset)))

    return skinID