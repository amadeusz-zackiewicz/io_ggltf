import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Scoops.Mesh import Triangles
from io_advanced_gltf2.Core.Bucket import Bucket

# https://docs.blender.org/api/current/bpy.types.Mesh.html
# https://docs.blender.org/api/current/bpy.types.Depsgraph.html
# https://docs.blender.org/api/current/bpy.types.Object.html
# https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get

def scoop_from_obj(
    bucket: Bucket,
    objAccessor,
    assignedID: int,
    normals = False,
    tangents = False,
    uvMaps = [],
    skinID = None,
    shapeKeys = [],
    shapeKeyNormals=False,
    vertexColors = [],
    mode = MESH_TYPE_TRIANGLES,
    maxBoneInfluences = 4,
):
    """Add mesh data using object's modifier stack

    Args:
        bucket (Bucket)
        obj (bpt.types.Object): Blender object that holds the mesh data
        normals (bool, optional): Should normals data be included. Defaults to False.
        tangents (bool, optional): Should the tangents data be included. Defaults to False.
        uvMaps (list of string, optional): Names of UV maps to include. Defaults to [].
        skinID (int, optional): Skin ID that will be used to get bone influences. Defaults to None.
        shapeKeys (list of int, optional): Names of shape keys to include. Defaults to [].
        vertexColors (list of int, optional): Names of vertex colors to include. Defaults to [].
        mode (int, optional): How the data should be stored inside the glTF file, please be aware that some functionality is unavailable for some modes. Defaults to MESH_TYPE_TRIANGLES.

    Returns:
        tuple: Tuple containing index of the mesh and weights (None if shape keys are not included)
    """
    # TODO: make sure every mesh mode is supported, only triangles for now
    obj = bpy.data.objects.get(objAccessor)
    Triangles.scoop_indexed(bucket, bucket.currentDependencyGraph.id_eval_get(obj).data, normals, obj.vertex_groups, uvMaps, vertexColors, shapeKeys, shapeKeyNormals, tangents, skinID, assignedID, maxInfluences=4)

# def scoop_base_mesh(
#     bucket,
#     mesh_name,
#     tangent = False,
#     uvMaps = None,
#     skin = True,
#     morphs = None,
#     mode = MESH_TYPE_TRIANGLES
# ):
#     return 0