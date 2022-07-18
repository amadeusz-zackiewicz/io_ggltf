from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Util import try_get_object
from io_advanced_gltf2.Core.Scoops import Skin
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
from io_advanced_gltf2.Core import BlenderUtil
import bpy

__setArmaturePoseCommand = lambda bucket, objGetter, poseMode: BlenderUtil.set_object_pose_mode(bucket=bucket, objName=objGetter, poseMode=poseMode)
__scoopSkinCommand = lambda bucket, skinID, objGetter, getInverse, boneBlackList, boneOffset: Skin.scoop_skin(bucket=bucket, objGetters=objGetter,getInversedBinds=getInverse, blacklist=boneBlackList, nodeIDOffset=boneOffset, skinID=skinID) # TODO: need to provide bone node offsets and skin id

def based_on_object(
    bucket: Bucket, 
    objName,
    getInverseBinds=False,
    forceRestPose=False,
    boneBlackList=[]
) -> int:
    
    try:
        obj = try_get_object(objName)
    except Exception:
        return None

    redundant, skinID = RM.smart_redundancy(bucket, (obj.name, obj.library), BUCKET_DATA_SKINS)

    if redundant:
        return skinID
    
    if forceRestPose:
        if obj.data.pose_position != BLENDER_ARMATURE_REST_MODE:
            bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__setArmaturePoseCommand, (bucket, objName, BLENDER_ARMATURE_REST_MODE)))
            bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__setArmaturePoseCommand, (bucket, objName, BLENDER_ARMATURE_POSE_MODE)))

    boneOffset = Skin.reserve_bone_ids(bucket, [(obj.name, obj.library)], boneBlackList) 
    bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, [(obj.name, obj.library)], getInverseBinds, boneBlackList, boneOffset)))
    return skinID


def based_on_object_modifiers(
    bucket: Bucket,
    objName,
    getInverseBinds=False,
    forceRestPose=False,
    boneBlackList=[]
) -> int:
    try:
        obj = try_get_object(objName)
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

    objectGetters = tuple([(o.name, o.library) for o in armatureObjects])

    redundant, skinID = RM.smart_redundancy(bucket, objectGetters, BUCKET_DATA_SKINS)

    if redundant:
        return skinID

    for armatureObj in armatureObjects:
        if forceRestPose:
            if armatureObj.data.pose_position != BLENDER_ARMATURE_REST_MODE:
                bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__setArmaturePoseCommand, (bucket, (armatureObj.name, armatureObj.library), BLENDER_ARMATURE_REST_MODE)))
                bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__setArmaturePoseCommand, (bucket, (armatureObj.name, armatureObj.library), BLENDER_ARMATURE_POSE_MODE)))

    boneOffset = Skin.reserve_bone_ids(bucket, objectGetters, boneBlackList) 
    bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, skinID, objectGetters, getInverseBinds, boneBlackList, boneOffset)))

    return skinID