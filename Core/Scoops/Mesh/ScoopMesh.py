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
    
    try:
        meshes = []
        objs = [bpy.data.objects.get(accessor) for accessor in objAccessors]
        targetMatrix = bpy.data.objects.get(mergeTargetAccessor).matrix_world

        meshes = [bucket.currentDependencyGraph.id_eval_get(obj).to_mesh() for obj in objs] # make copies of the meshes

        Triangles.scoop_indexed_and_merge(bucket, 
        meshes, 
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
    finally:
        # clear all mesh copies from memory
        for m in meshes:
            del m
        del meshes