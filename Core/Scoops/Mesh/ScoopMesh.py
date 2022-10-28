import bpy
from io_ggltf.Constants import *
from io_ggltf.Core.Scoops.Mesh import Triangles
from io_ggltf.Core.Bucket import Bucket

def scoop_and_merge(
    bucket: Bucket,
    objAccessors,
    mergeTargetAccessor,
    name,
    assignedID,
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
    objs = [bpy.data.objects.get(accessor) for accessor in objAccessors]
    targetMatrix = bpy.data.objects.get(mergeTargetAccessor).matrix_world

    Triangles.scoop_indexed_and_merge(bucket, 
    [bucket.currentDependencyGraph.id_eval_get(obj).data for obj in objs], 
    [obj.matrix_world for obj in objs], 
    name, 
    targetMatrix, 
    normals, 
    [obj.vertex_groups for obj in objs], 
    uvMaps, 
    vertexColors, 
    shapeKeys, 
    shapeKeyNormals, 
    tangents, 
    skinID, 
    assignedID, 
    maxBoneInfluences
    )