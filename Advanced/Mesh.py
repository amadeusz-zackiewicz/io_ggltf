from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
from io_advanced_gltf2.Core import BlenderUtil
from io_advanced_gltf2.Core.Util import try_get_object
from io_advanced_gltf2.Core.Scoops.Mesh import ScoopMesh
from io_advanced_gltf2.Advanced import Settings
import bpy

__disable_armature_modifier = lambda bucket, objAccessor, modifierID: BlenderUtil.set_object_modifier(bucket=bucket, objAccessor=objAccessor, modifierID=modifierID, setActive=False)
__enable_armature_modifier = lambda bucket, objAccessor, modifierID: BlenderUtil.set_object_modifier(bucket=bucket, objAccessor=objAccessor, modifierID=modifierID, setActive=True)
__scoop_mesh_command = lambda bucket, objAccessor, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, maxBones: ScoopMesh.scoop_from_obj(bucket=bucket, objAccessor=objAccessor, normals=normals, tangents=tangents, uvMaps=uvMaps, vertexColors=vertexColors, skinID=skinID, shapeKeys=shapeKeys, shapeKeyNormals=shapeKeyNormals, maxBoneInfluences=maxBones, assignedID=meshID)
#TODO: implement rest of the settings on scoops

def based_on_object(bucket: Bucket, objAccessor,
normals=None,
tangents=None,
uvMaps=[],
vertexColors=[],
boneInfluences=None,
skinID=None,
shapeKeys=[],
shapeKeyNormals=None,
shapeKeyTangents=None,
shapeKeyUVs=None,
checkRedundancy=None
) -> int:

    if normals == None:
        normals = bucket.settings[BUCKET_SETTING_MESH_GET_NORMALS]
    if tangents == None:
        tangents = bucket.settings[BUCKET_SETTING_MESH_GET_TANGENTS]
    if boneInfluences == None:
        boneInfluences = bucket.settings[BUCKET_SETTING_MESH_GET_BONE_INFLUENCE]
    if shapeKeyNormals == None:
        shapeKeyNormals = bucket.settings[BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS]
    if shapeKeyTangents == None:
        shapeKeyTangents = bucket.settings[BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS]
    if shapeKeyUVs == None:
        shapeKeyUVs = bucket.settings[BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV]
    if checkRedundancy == None:
        checkRedundancy = bucket.settings[BUCKET_SETTING_REDUNDANCY_CHECK_MESH]

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None
    
    if checkRedundancy:
        redundant, meshID = RM.smart_redundancy(bucket, BlenderUtil.get_object_accessor(obj), BUCKET_DATA_MESHES)

        if redundant:
            return meshID
    else:
        meshID = RM.reserve_untracked_id(bucket, BUCKET_DATA_MESHES)

    for i, mod in enumerate(obj.modifiers):
        if mod.type == BLENDER_MODIFIER_ARMATURE:
            bucket.commandQueue[COMMAND_QUEUE_SETUP].append((__disable_armature_modifier,(bucket, BlenderUtil.get_object_accessor(obj), i)))
            bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP].append((__enable_armature_modifier, (bucket, BlenderUtil.get_object_accessor(obj), i)))
    
    bucket.commandQueue[COMMAND_QUEUE_MESH].append((__scoop_mesh_command, (bucket, BlenderUtil.get_object_accessor(obj), normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, Settings.get_setting(bucket, BUCKET_SETTING_MESH_MAX_BONES) if boneInfluences else 0)))

    return meshID
        