from json.encoder import INFINITY
import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Core.Managers import AccessorManager

# https://docs.blender.org/api/current/bpy.types.Mesh.html
# https://docs.blender.org/api/current/bpy.types.Depsgraph.html
# https://docs.blender.org/api/current/bpy.types.Object.html
# https://docs.blender.org/api/current/bpy.types.ID.html#bpy.types.ID.evaluated_get

def scoop_from_obj(
    bucket,
    obj,
    tangent = False,
    uvMaps = None,
    skin = True,
    morphs = None,
    mode = MESH_TYPE_TRIANGLES
):
    dependencyGraph = bpy.context.evaluated_depsgraph_get()
    return __scoop_triangles(bucket, dependencyGraph.id_eval_get(obj).data, None, None, False)

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

# how to generate names:
#
# mesh name:            <original.name>.<hex(depsgraph_ID)>.<mode>
# accessor name:        <original.name>.<hex(depsgraph_ID)>.<mode>.<primitive>.<attribute>
#
# if the attribute is not dynamic, for example POSITION or NORMAL, 
# use the attribute type itself, for dynamic attributes such
# as UV maps or weight use the same name as blender
# for example:
# cube.0x1234.0.4.POSITION or cube.0x1234.0.4.uv_map_final
#
# Q: why the hex()?
# A: looks cooler then pure int

def __get_core_mesh_components(bucket, mesh):
    """
    Gets vertices, normals, indices and min max boundary
    returns a tuple of (positions, normals, vertices, min, max)
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
        for v in vertices: # should always be 3
            indices.append(v)

    return (positions, normals, indices, _min, _max)


def __scoop_triangles(bucket, meshObj, uvMaps, morphs, skin):

    originalName = meshObj.original.name
    depsID = str(hex(id(meshObj)))

    trackerName = ".".join([originalName, depsID, str(MESH_TYPE_TRIANGLES)])

    if trackerName in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][trackerName]

    positions, normals, indices, min, max = __get_core_mesh_components(bucket, meshObj)

    accessors = {
        GEOMETRY_ATTRIBUTE_STR_POSITION: AccessorManager.add_accessor(bucket, 
        ACCESSOR_COMPONENT_TYPE_FLOAT, 
        ACCESSOR_TYPE_VECTOR_3,
        PACKING_FORMAT_FLOAT, 
        positions, min, max
        ),
        GEOMETRY_ATTRIBUTE_STR_NORMAL: AccessorManager.add_accessor(bucket,
        ACCESSOR_COMPONENT_TYPE_FLOAT, 
        ACCESSOR_TYPE_VECTOR_3, 
        PACKING_FORMAT_FLOAT,
        normals
        )
    }

    indicesAccess = AccessorManager.add_accessor(bucket, 
    ACCESSOR_COMPONENT_TYPE_UNSIGNED_INT,
    ACCESSOR_TYPE_SCALAR,
    PACKING_FORMAT_U_INT,
    indices
    )

    meshDict = {
        MESH_NAME: originalName,
        MESH_PRIMITIVES:[{
            MESH_PRIMITIVE_ATTRIBUTES: accessors,
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0, #TODO: ensure materials are correctly assigned here
            MESH_PRIMITIVE_INDICES: indicesAccess
        }]
        }

    meshID = len(bucket.data[BUCKET_DATA_MESHES])

    bucket.data[BUCKET_DATA_MESHES].append(meshDict)
    bucket.trackers[BUCKET_TRACKER_MESHES][trackerName] = meshID

    # TODO: accessors are still not tracked

    return meshID
    