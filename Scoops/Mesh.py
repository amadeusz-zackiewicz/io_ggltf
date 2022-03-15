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
    return __scoop_mesh_triangles(bucket, dependencyGraph.id_eval_get(obj).data, uvMaps, vertexColors, shapeKeys, tangents, skin)

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

def __decompose_blender_mesh(bucket, mesh):
    """
    Calculates splits and normals then gets vertices, normals, 
    indices and material indices
    returns a tuple of (positions, normals, indices, materialIndex)
    """

    mesh.calc_normals_split()
    mesh.calc_loop_triangles()

    positions = []
    normals = []
    indices = []
    materialIndex = []

    for v in mesh.vertices:
        v = Util.location_ensure_coord_space(bucket, v.co)
        positions.append(v)

    for v in mesh.vertices:
        v = Util.direction_ensure_coord_space(bucket, v.normal)
        normals.append(v)
    
    for l in mesh.loop_triangles:
        vertices = l.vertices
        materialIndex.append(l.material_index)
        for v in vertices: # should always be 3
            indices.append(v)

    return (positions, normals, indices, materialIndex)


def __scoop_mesh_triangles(bucket, meshObj, uvMaps, vertexColors, shapeKeys, tangents, skin):

    originalName = meshObj.original.name
    depsID = id(meshObj)

    tracker = Tracer.make_mesh_tracker(originalName, depsID, MESH_TYPE_TRIANGLES, uvMaps, vertexColors, shapeKeys, tangents, skin)

    if tracker in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][tracker]

    positions, normals, indices, materialIndex = __decompose_blender_mesh(bucket, meshObj)

    # create a primitive for each material
    primitive_count = len(meshObj.materials) 

    if primitive_count == 0: primitive_count = 1 # make sure we get at least one primitive

    class primitives: pass
    primitives.positions = []
    primitives.normals = []
    primitives.indices = []
    primitives.duplicates = []

    for i in range(0, primitive_count):
        primitives.positions.append([])
        primitives.normals.append([])
        primitives.indices.append([])
        primitives.duplicates.append({})

    # convert indices from mesh to primitive local indices
    for i, m in enumerate(materialIndex):
        def add_index(index):
            if index in primitives.duplicates[m]:
                primitives.indices[m].append(primitives.duplicates[m][index])
            else:
                l = len(primitives.positions[m])
                primitives.positions[m].append(positions[index])
                primitives.normals[m].append(normals[index])
                primitives.indices[m].append(l)
                primitives.duplicates[m][index] = l

        stride = i * 3
        index1 = indices[stride]
        index2 = indices[stride + 1]
        index3 = indices[stride + 2]

        add_index(index1)
        add_index(index2)
        add_index(index3)

    meshDict = {
        MESH_NAME: tracker,
        MESH_PRIMITIVES: []
        }

    for i in range(0, primitive_count):

        _min = [100000.0, 100000.0, 100000.0]
        _max = [-100000.0, -100000.0, -100000.0]

        print(len(positions))

        for p in primitives.positions[i]:
            print(i)
            _min[0] = min(_min[0], p.x)
            _min[1] = min(_min[1], p.y)
            _min[2] = min(_min[2], p.z)

            _max[0] = max(_max[0], p.x)
            _max[1] = max(_max[1], p.y)
            _max[2] = max(_max[2], p.z)

        positionsAccessor = __get_accessor_positions(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, primitives.positions[i], _min, _max)
        normalsAccessor = __get_accessor_normals(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, primitives.normals[i])
        indicesAccessor = __get_accessor_indices(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, primitives.indices[i])

        accessors = {
            MESH_ATTRIBUTE_STR_POSITION: positionsAccessor,
            MESH_ATTRIBUTE_STR_NORMAL: normalsAccessor
        }

        meshDict[MESH_PRIMITIVES].append({
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0, # TODO: materials are not yet supported
            MESH_PRIMITIVE_ATTRIBUTES: accessors,
            MESH_PRIMITIVE_INDICES: indicesAccessor
        })

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