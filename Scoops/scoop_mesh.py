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

def __scoop_triangles(bucket, meshObj, uvMaps, morphs, skin):

    originalName = meshObj.original.name
    depsID = str(hex(id(meshObj)))

    trackerName = ".".join([originalName, depsID, str(MESH_TYPE_TRIANGLES)])

    if trackerName in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][trackerName]

    meshObj.calc_loop_triangles()
    meshObj.calc_normals_split()
    meshObj.calc_normals()

    positions = []
    normals = []
    indices = []

    min = [-1, -1, -1]
    max = [1, 1, 1]

    for v in meshObj.vertices:
        v = Util.location_ensure_coord_space(bucket, v.co)
        positions.append(v)

    for v in meshObj.vertices:
        v = Util.direction_ensure_coord_space(bucket, v.normal)
        normals.append(v)

    
    for l in meshObj.loop_triangles:
        vertices = l.vertices
        for v in vertices: # should always be 3
            indices.append(v)

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
        MESH_NAME: trackerName,
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
    