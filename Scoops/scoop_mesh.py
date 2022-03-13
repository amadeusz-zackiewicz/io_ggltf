from json.encoder import INFINITY
import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Core.Managers import AccessorManager, Tracer

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
    return __scoop_triangles(bucket, dependencyGraph.id_eval_get(obj).data, uvMaps, vertexColors, shapeKeys, tangents, skin)

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

def __get_core_mesh_components(bucket, mesh):
def __decompose_blender_mesh(bucket, mesh):
    """
    Calculates splits and normals then gets vertices, normals, 
    indices and min max boundary
    returns a tuple of (positions, normals, indices, min, max)
    """

    mesh.calc_normals_split()
    mesh.calc_loop_triangles()

    positions = []
    normals = []
    indices = []

    _min = [INFINITY, INFINITY, INFINITY]
    _max = [-INFINITY, -INFINITY, -INFINITY]

    for v in mesh.vertices:
        v = Util.location_ensure_coord_space(bucket, v.co)

        _min[0] = min(_min[0], v[0])
        _min[1] = min(_min[1], v[1])
        _min[2] = min(_min[2], v[2])

        _max[0] = max(_max[0], v[0])
        _max[1] = max(_max[1], v[1])
        _max[2] = max(_max[2], v[2])

        positions.append(v)

    for v in mesh.vertices:
        v = Util.direction_ensure_coord_space(bucket, v.normal)
        normals.append(v)
    
    for l in mesh.loop_triangles:
        vertices = l.vertices
        materialIndex.append(l.material_index)
        for v in vertices: # should always be 3
            indices.append(v)

    return (positions, normals, indices, materialIndex, _min, _max)


def __scoop_triangles(bucket, meshObj, uvMaps, vertexColors, shapeKeys, tangents, skin):

    originalName = meshObj.original.name
    depsID = id(meshObj)

    tracker = Tracer.make_mesh_tracker(originalName, depsID, MESH_TYPE_TRIANGLES, uvMaps, vertexColors, shapeKeys, tangents, skin)

    if tracker in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][tracker]

    positions, normals, indices, min, max = __get_core_mesh_components(bucket, meshObj)
    positions, normals, indices, materialIndex, min, max = __decompose_blender_mesh(bucket, meshObj)

    positionsAccessor = __get_accessor_positions(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, 0, positions, min, max)
    normalsAccessor = __get_accessor_normals(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, 0, normals)

    accessors = {
        MESH_ATTRIBUTE_STR_POSITION: positionsAccessor,
        MESH_ATTRIBUTE_STR_NORMAL: normalsAccessor
    }

    meshDict = {
        MESH_NAME: tracker,
        MESH_PRIMITIVES:[{
            MESH_PRIMITIVE_ATTRIBUTES: accessors,
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0, #TODO: ensure materials are correctly assigned here
            MESH_PRIMITIVE_INDICES: __get_accessor_indices(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, 0, indices)
        }]
        }

    meshID = len(bucket.data[BUCKET_DATA_MESHES])

    bucket.data[BUCKET_DATA_MESHES].append(meshDict)
    bucket.trackers[BUCKET_TRACKER_MESHES][tracker] = meshID

    return meshID
    
def __get_accessor_positions(bucket, meshName, depsgraphID, mode, primitive, positions, min, max) -> int:

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, MESH_TYPE_TRIANGLES, 0, MESH_ATTRIBUTE_STR_POSITION)
    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, MESH_ATTRIBUTE_STR_POSITION)

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_3,
    PACKING_FORMAT_FLOAT,
    data=positions,
    tracker=tracker,
    min=min,
    max=max,
    name=tracker # TODO: this should not be in release build
    )

def __get_accessor_normals(bucket, meshName, depsgraphID, mode, primitive, normals) -> int:

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, MESH_TYPE_TRIANGLES, primitive, MESH_ATTRIBUTE_STR_NORMAL)
    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, MESH_ATTRIBUTE_STR_NORMAL)

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_3,
    PACKING_FORMAT_FLOAT,
    data=normals,
    tracker=tracker,
    name=tracker # TODO: this should not be in release build
    )

def __get_accessor_indices(bucket, meshName, depsgraphID, mode, primitive, indices) -> int:

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, MESH_TYPE_TRIANGLES, primitive, MESH_PRIMITIVE_INDICES.upper())
    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, MESH_PRIMITIVE_INDICES.upper())

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_UNSIGNED_INT,
    ACCESSOR_TYPE_SCALAR,
    PACKING_FORMAT_U_INT,
    data=indices,
    tracker=tracker,
    name=tracker # TODO: this should not be in release build
    )