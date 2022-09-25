from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Managers import RedundancyManager as RM
from io_ggltf.Core import BlenderUtil
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core.Scoops.Mesh import ScoopMesh
from io_ggltf.Advanced import Settings, Linker
import bpy

__scoop_merged_command = lambda bucket, objAccessors, mergeTargetAccessor, name, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, maxBones: ScoopMesh.scoop_and_merge(bucket=bucket, objAccessors=objAccessors, mergeTargetAccessor=mergeTargetAccessor,assignedID=meshID, normals=normals, tangents=tangents, uvMaps=uvMaps, shapeKeys=shapeKeys, shapeKeyNormals=shapeKeyNormals, vertexColors=vertexColors, maxBoneInfluences=maxBones, skinID=skinID, name=name)
__scoop_mesh_command = lambda bucket, objAccessor, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, maxBones: ScoopMesh.scoop_from_obj(bucket=bucket, objAccessor=objAccessor, normals=normals, tangents=tangents, uvMaps=uvMaps, vertexColors=vertexColors, skinID=skinID, shapeKeys=shapeKeys, shapeKeyNormals=shapeKeyNormals, maxBoneInfluences=maxBones, assignedID=meshID)


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
checkRedundancy=None,
autoLink=None
) -> int:

    if normals == None:
        normals = bucket.settings[__k.BUCKET_SETTING_MESH_GET_NORMALS]
    if tangents == None:
        tangents = bucket.settings[__k.BUCKET_SETTING_MESH_GET_TANGENTS]
    if boneInfluences == None:
        boneInfluences = bucket.settings[__k.BUCKET_SETTING_MESH_GET_BONE_INFLUENCE]
    if shapeKeyNormals == None:
        shapeKeyNormals = bucket.settings[__k.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS]
    if shapeKeyTangents == None:
        shapeKeyTangents = bucket.settings[__k.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS]
    if shapeKeyUVs == None:
        shapeKeyUVs = bucket.settings[__k.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV]
    if checkRedundancy == None:
        checkRedundancy = bucket.settings[__k.BUCKET_SETTING_REDUNDANCY_CHECK_MESH]
    if autoLink == None:
        autoLink = bucket.settings[__k.BUCKET_SETTING_MESH_AUTO_LINK]

    try:
        obj = try_get_object(objAccessor)
    except Exception:
        return None
    
    if checkRedundancy:
        redundant, meshID = RM.register_unique(bucket, BlenderUtil.get_object_accessor(obj), __k.BUCKET_DATA_MESHES)

        if redundant:
            return meshID
    else:
        meshID = RM.register_unsafe(bucket, BlenderUtil.get_object_accessor(obj), __k.BUCKET_DATA_MESHES)

    BlenderUtil.queue_reset_modifier_changes(bucket, obj, __k.BLENDER_MODIFIER_ARMATURE)
    BlenderUtil.queue_disable_modifier_type(bucket, obj, __k.BLENDER_MODIFIER_ARMATURE, __k.COMMAND_QUEUE_MESH)
    BlenderUtil.queue_update_depsgraph(bucket, __k.COMMAND_QUEUE_MESH)
    
    bucket.commandQueue[__k.COMMAND_QUEUE_MESH].append((__scoop_mesh_command, (bucket, BlenderUtil.get_object_accessor(obj), normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, Settings.get_setting(bucket, __k.BUCKET_SETTING_MESH_MAX_BONES) if boneInfluences else 0)))

    if autoLink:
        Linker.mesh_to_unsafe_node(bucket, meshID, BlenderUtil.get_object_accessor(obj))

    return meshID

def merged_based_on_hierarchy(bucket: Bucket,
topObjectAccessor,
blacklist = {},
name="NewMesh",
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
autoLink=None
) -> int:
    def collect_mesh_objects(currentObject, collected: list, blacklist):
        if currentObject.name in blacklist:
            return

        for c in currentObject.children:
            collect_mesh_objects(c, collected, blacklist)

        if currentObject.type == __k.BLENDER_TYPE_MESH:
            collected.append(currentObject)

    if normals == None:
        normals = bucket.settings[__k.BUCKET_SETTING_MESH_GET_NORMALS]
    if tangents == None:
        tangents = bucket.settings[__k.BUCKET_SETTING_MESH_GET_TANGENTS]
    if boneInfluences == None:
        boneInfluences = bucket.settings[__k.BUCKET_SETTING_MESH_GET_BONE_INFLUENCE]
    if shapeKeyNormals == None:
        shapeKeyNormals = bucket.settings[__k.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS]
    if shapeKeyTangents == None:
        shapeKeyTangents = bucket.settings[__k.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS]
    if shapeKeyUVs == None:
        shapeKeyUVs = bucket.settings[__k.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV]
    if autoLink == None:
        autoLink = bucket.settings[__k.BUCKET_SETTING_MESH_AUTO_LINK]

    topObj = try_get_object(topObjectAccessor)

    meshObjects = []

    collect_mesh_objects(topObj, meshObjects, blacklist)

    if len(meshObjects) > 0:
        if len(uvMaps) > 0:
            for obj in meshObjects:
                if not BlenderUtil.object_has_uv_maps(obj, uvMaps):
                    print(f"Mesh.merged_based_on_hierarchy aborted: {obj.name} does not contain specified UV Maps")
                    return None
        if len(vertexColors) > 0:
            for obj in meshObjects:
                if not BlenderUtil.object_has_vertex_colors(obj, vertexColors):
                    print(f"Mesh.merged_based_on_hierarchy aborted: {obj.name} does not contain specified Vertex Colors")
                    return None
        if len(shapeKeys) > 0:
            for obj in meshObjects:
                if not BlenderUtil.object_has_shape_keys(obj, shapeKeys):
                    print(f"Mesh.merged_based_on_hierarchy aborted: {obj.name} does not contain specified Shape Keys")
                    return None

        meshID = RM.register_unsafe(bucket, [BlenderUtil.get_object_accessor(o) for o in meshObjects], __k.BUCKET_DATA_MESHES)

        for obj in meshObjects:
            BlenderUtil.queue_reset_modifier_changes(bucket, obj, __k.BLENDER_MODIFIER_ARMATURE)
            BlenderUtil.queue_disable_modifier_type(bucket, obj, __k.BLENDER_MODIFIER_ARMATURE, __k.COMMAND_QUEUE_MESH)
            
        BlenderUtil.queue_update_depsgraph(bucket, __k.COMMAND_QUEUE_MESH)
        
        bucket.commandQueue[__k.COMMAND_QUEUE_MESH].append((__scoop_merged_command, (bucket, [BlenderUtil.get_object_accessor(obj) for obj in meshObjects], BlenderUtil.get_object_accessor(topObj), name, normals, tangents, uvMaps, vertexColors, skinID, shapeKeys, shapeKeyNormals, meshID, Settings.get_setting(bucket, __k.BUCKET_SETTING_MESH_MAX_BONES) if boneInfluences else 0)))
        
        if autoLink:
            Linker.mesh_to_unsafe_node(bucket, meshID, BlenderUtil.get_object_accessor(obj))

        return meshID
    else:
        print(f"No meshes found under hierarchy of: {BlenderUtil.get_object_accessor(obj)}")
        return None

