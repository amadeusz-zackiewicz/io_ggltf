import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops.Mesh import Triangles

# https://docs.blender.org/api/current/bpy.types.Mesh.html
# https://docs.blender.org/api/current/bpy.types.Depsgraph.html
# https://docs.blender.org/api/current/bpy.types.Object.html
# https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get

def scoop_from_obj(
    bucket,
    obj,
    tangents = False,
    uvMaps = [],
    skin = True,
    shapeKeys = [],
    vertexColors = [],
    mode = MESH_TYPE_TRIANGLES
):
    # TODO: make sure every mesh mode is supported, only triangles for now
    dependencyGraph = bpy.context.evaluated_depsgraph_get()
    return Triangles.scoop_indexed(bucket, dependencyGraph.id_eval_get(obj).data, uvMaps, vertexColors, shapeKeys, tangents, skin)

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