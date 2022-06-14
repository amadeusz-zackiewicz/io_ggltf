from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Util import try_get_object
from io_advanced_gltf2.Core.Scoops import Skin
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
from io_advanced_gltf2.Core import BlenderUtil
import bpy

__setArmaturePoseCommand = lambda bucket, objName, poseMode: BlenderUtil.set_object_pose_mode(bucket=bucket, objName=objName, poseMode=poseMode)
__scoopSkinCommand = lambda bucket, obj, getInverse, boneBlackList: Skin.scoop_skin(bucket=bucket, obj=obj,getInversedBinds=getInverse, blacklist=boneBlackList)

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
    else:
        redundant, skinID = RM.smart_redundancy(bucket, obj, BUCKET_DATA_SKINS)

        if redundant:
            return skinID
        else:
            if forceRestPose:
                if obj.data.pose_position != BLENDER_ARMATURE_REST_MODE:
                    bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__setArmaturePoseCommand, (bucket, objName, BLENDER_ARMATURE_REST_MODE)))
                    
            bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__setArmaturePoseCommand, (bucket, objName, obj.data.pose_position)))

            bucket.commandQueue[COMMAND_QUEUE_SKIN].append((__scoopSkinCommand, (bucket, obj, getInverseBinds, boneBlackList)))
            return skinID


def based_on_mesh_modifiers(
    bucket: Bucket,
    objName,
    getInverseBinds=False,
    forceRestPose=False,
    boneBlackList=[]
):
    obj = try_get_object(objName)

    armatureDataBlocks = []
    depsGraph = bucket.currentDependencyGraph

    for mod in obj.modifiers:
        if mod.type == BLENDER_MODIFIER_ARMATURE:
            if depsGraph.mode == BLENDER_DEPSGRAPH_MODE_VIEWPORT and mod.show_viewport:
                armatureDataBlocks.append(mod.object)
            if depsGraph.mode == BLENDER_DEPSGRAPH_MODE_RENDER and mod.show_render:
                armatureDataBlocks.append(mod.object)

    if len(armatureDataBlocks) == 0:
        print("No armature modifiers found")
        return None

    redundant, skinID = RM.smart_redundancy(bucket, armatureDataBlocks, BUCKET_DATA_SKINS)

    # TODO: check for redudnancy and queue commands