from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import BlenderUtil, Util
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.Scoops.Mesh import ScoopMesh
from io_ggltf.Advanced import Settings, Attach
from io_ggltf.Core.Validation import MeshValidation
import bpy
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI

__scoop_merged_command = lambda bucket, objAccessors, mergeTargetAccessor, name, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, maxBones: ScoopMesh.scoop_and_merge(bucket=bucket, objAccessors=objAccessors, mergeTargetAccessor=mergeTargetAccessor,assignedID=meshID, normals=normals, tangents=tangents, uvMaps=uvMaps, shapeKeys=shapeKeys, shapeKeyNormals=shapeKeyNormals, vertexColors=vertexColors, maxBoneInfluences=maxBones, skinID=skinID, name=name)
__scoop_mesh_command = lambda bucket, objAccessor, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, maxBones, name: ScoopMesh.scoop_from_obj(bucket=bucket, objAccessor=objAccessor, normals=normals, tangents=tangents, uvMaps=uvMaps, vertexColors=vertexColors, skinID=skinID, shapeKeys=shapeKeys, shapeKeyNormals=shapeKeyNormals, maxBoneInfluences=maxBones, assignedID=meshID, name=name)

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Mesh-Module#based_on_object")
def based_on_object(bucket: Bucket, objAccessor,
normals=None,
tangents=None,
uvMaps=[],
vertexColors=[],
boneInfluenceCount=None,
skinID=None,
shapeKeys=[],
shapeKeyNormals=None,
shapeKeyTangents=None,
shapeKeyUVs=None,
checkRedundancy=None,
autoAttach=None,
name=None,
origin=None
) -> int:
    """Get the mesh as seen in viewport"""

    if normals == None:
        normals = bucket.settings[__c.BUCKET_SETTING_MESH_GET_NORMALS]
    if tangents == None:
        tangents = bucket.settings[__c.BUCKET_SETTING_MESH_GET_TANGENTS]
    if skinID != None:
        if boneInfluenceCount == None:
            boneInfluenceCount = bucket.settings[__c.BUCKET_SETTING_MESH_MAX_BONES]
    else:
        boneInfluenceCount = 0
    if shapeKeyNormals == None:
        shapeKeyNormals = bucket.settings[__c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS]
    if shapeKeyTangents == None:
        shapeKeyTangents = bucket.settings[__c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS]
    if shapeKeyUVs == None:
        shapeKeyUVs = bucket.settings[__c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV]
    if checkRedundancy == None:
        checkRedundancy = bucket.settings[__c.BUCKET_SETTING_REDUNDANCY_CHECK_MESH]
    if autoAttach == None:
        autoAttach = bucket.settings[__c.BUCKET_SETTING_MESH_AUTO_ATTACH]

    try:
        obj = [try_get_object(objAccessor)]
    except Exception:
        return None

    MeshValidation.validate_meshes(obj)
    MeshValidation.validate_uv_maps(obj, uvMaps)
    MeshValidation.validate_vertex_colors(obj, vertexColors)
    MeshValidation.validate_shape_keys(obj, shapeKeys)
    
    if checkRedundancy:
        redundant, meshID = RM.register_unique(bucket, BlenderUtil.get_object_accessor(obj[0]), __c.BUCKET_DATA_MESHES)

        if redundant:
            return meshID
    else:
        meshID = RM.register_unsafe(bucket, BlenderUtil.get_object_accessor(obj[0]), __c.BUCKET_DATA_MESHES)

    BlenderUtil.queue_reset_modifier_changes(bucket, obj[0], __c.BLENDER_MODIFIER_ARMATURE)
    BlenderUtil.queue_disable_modifier_type(bucket, obj[0], __c.BLENDER_MODIFIER_ARMATURE, __c.COMMAND_QUEUE_MESH)
    BlenderUtil.queue_update_depsgraph(bucket, __c.COMMAND_QUEUE_MESH)

    if name == None:
        name = obj[0].data.name

    if origin == None:
        origin = BlenderUtil.get_object_accessor(obj[0])
    
    bucket.commandQueue[__c.COMMAND_QUEUE_MESH].append((__scoop_merged_command, (bucket, [BlenderUtil.get_object_accessor(obj[0])], origin, name, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, boneInfluenceCount)))
    #bucket.commandQueue[__c.COMMAND_QUEUE_MESH].append((__scoop_mesh_command, (bucket, BlenderUtil.get_object_accessor(obj), normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, Settings.get_setting(bucket, __c.BUCKET_SETTING_MESH_MAX_BONES) if boneInfluenceCount else 0, name)))

    if autoAttach:
        Attach.mesh_to_unsafe_node(bucket, meshID, BlenderUtil.get_object_accessor(obj[0]))

    return meshID

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Mesh-Module#merged_based_on_hierarchy")
def merged_based_on_hierarchy(bucket: Bucket,
topObjectAccessor,
blacklist = {},
name="NewMesh",
normals=None,
tangents=None,
uvMaps=[],
vertexColors=[],
boneInfluenceCount=None,
skinID=None,
shapeKeys=[],
shapeKeyNormals=None,
shapeKeyTangents=None,
shapeKeyUVs=None,
filters=[],
autoAttach=None,
origin=None
) -> int:
    """Merge all the meshes in the hierarchy into one, using a custom origin point (top object by default). 
    In case of UV maps, vertex colors and shape keys, all meshes must contain each one specified"""

    def collect_mesh_objects(currentObject, collected: list, blacklist, filters):
        if currentObject.name in blacklist or not Util.name_passes_filters(filters, currentObject.name):
            return

        for c in currentObject.children:
            collect_mesh_objects(c, collected, blacklist, filters)

        if currentObject.type == __c.BLENDER_TYPE_MESH:
            collected.append(currentObject)

    if normals == None:
        normals = bucket.settings[__c.BUCKET_SETTING_MESH_GET_NORMALS]
    if tangents == None:
        tangents = bucket.settings[__c.BUCKET_SETTING_MESH_GET_TANGENTS]
    if skinID != None:
        if boneInfluenceCount == None:
            boneInfluenceCount = bucket.settings[__c.BUCKET_SETTING_MESH_MAX_BONES]
    else:
        boneInfluenceCount = 0
    if shapeKeyNormals == None:
        shapeKeyNormals = bucket.settings[__c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS]
    if shapeKeyTangents == None:
        shapeKeyTangents = bucket.settings[__c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS]
    if shapeKeyUVs == None:
        shapeKeyUVs = bucket.settings[__c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV]
    if autoAttach == None:
        autoAttach = bucket.settings[__c.BUCKET_SETTING_MESH_AUTO_ATTACH]

    topObj = try_get_object(topObjectAccessor)

    meshObjects = []

    collect_mesh_objects(topObj, meshObjects, blacklist, filters)

    if len(meshObjects) > 0:
        
        MeshValidation.validate_meshes(meshObjects)
        MeshValidation.validate_uv_maps(meshObjects, uvMaps)
        MeshValidation.validate_vertex_colors(meshObjects, vertexColors)
        MeshValidation.validate_shape_keys(meshObjects, shapeKeys)

        meshID = RM.register_unsafe(bucket, [BlenderUtil.get_object_accessor(o) for o in meshObjects], __c.BUCKET_DATA_MESHES)

        for obj in meshObjects:
            BlenderUtil.queue_reset_modifier_changes(bucket, obj, __c.BLENDER_MODIFIER_ARMATURE)
            BlenderUtil.queue_disable_modifier_type(bucket, obj, __c.BLENDER_MODIFIER_ARMATURE, __c.COMMAND_QUEUE_MESH)
            
        BlenderUtil.queue_update_depsgraph(bucket, __c.COMMAND_QUEUE_MESH)
        
        if origin == None:
            origin = BlenderUtil.get_object_accessor(topObj)
        else:
            originObj = try_get_object(origin)
            origin = BlenderUtil.get_object_accessor(originObj)

        bucket.commandQueue[__c.COMMAND_QUEUE_MESH].append((__scoop_merged_command, (bucket, [BlenderUtil.get_object_accessor(obj) for obj in meshObjects], origin, name, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, boneInfluenceCount)))
        
        if autoAttach:
            Attach.mesh_to_unsafe_node(bucket, meshID, origin)

        return meshID
    else:
        print(f"No meshes found under hierarchy of: {BlenderUtil.get_object_accessor(topObj)}")
        return None

