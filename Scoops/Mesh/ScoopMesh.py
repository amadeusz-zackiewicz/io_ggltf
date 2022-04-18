import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops.Mesh import Triangles
from io_advanced_gltf2.Core.Bucket import Bucket

# https://docs.blender.org/api/current/bpy.types.Mesh.html
# https://docs.blender.org/api/current/bpy.types.Depsgraph.html
# https://docs.blender.org/api/current/bpy.types.Object.html
# https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get

def scoop_from_obj(
    bucket: Bucket,
    obj,
    tangents = False,
    uvMaps = [],
    skinID = None,
    shapeKeys = [],
    vertexColors = [],
    mode = MESH_TYPE_TRIANGLES
):
    # TODO: make sure every mesh mode is supported, only triangles for now
    return Triangles.scoop_indexed(bucket, bucket.currentDependencyGraph.id_eval_get(obj).data, obj.vertex_groups, uvMaps, vertexColors, shapeKeys, tangents, skinID, maxInfluences=4)

def scoop_base_mesh(
    bucket,
    mesh_name,
    tangent = False,
    uvMaps = None,
    skin = True,
    morphs = None,
    mode = MESH_TYPE_TRIANGLES
):
    return 0