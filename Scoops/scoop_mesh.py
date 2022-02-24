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
# mesh name:            <original.name>.<hex(depsgraph_ID)>
# buffer name:          <original.name>.<hex(depsgraph_ID)>
# buffer view name:     <original.name>.<hex(depsgraph_ID)>.<attribute>
# accessor name:        <original.name>.<hex(depsgraph_ID)>.<attribute>
#
# if the attribute is not dynamic, for example POSITION or NORMAL, 
# use the attribute type itself, for dynamic attributes such
# as UV maps or weight use the same name as blender
# for example:
# cube.0x1234.POSITION or cube.0x1234.uv_map_final
#
# Q: why the hex()?
# A: looks cooler then pure int

def __scoop_triangles(bucket, meshObj, uvMaps, morphs, skin):
 
    originalName = meshObj.original.name
    depsID = str(hex(id(meshObj)))

    tracker_name = ".".join([originalName, depsID])

    if tracker_name in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][tracker_name]


    positions = []
    normals = []

    for v in meshObj.vertices:
        v = Util.location_ensure_coord_space(bucket, v.co)
        positions.append(v)

    for v in meshObj.vertices:
        v = Util.direction_ensure_coord_space(bucket, v.normal)
        normals.append(v)

    accessors = {
        GEOMETRY_ATTRIBUTE_STR_POSITION: AccessorManager.add_accessor(bucket, 
        ACCESSOR_COMPONENT_TYPE_FLOAT, 
        ACCESSOR_TYPE_VECTOR_3,
        PACKING_FORMAT_FLOAT, 
        positions),
        GEOMETRY_ATTRIBUTE_STR_NORMAL: AccessorManager.add_accessor(bucket,
        ACCESSOR_COMPONENT_TYPE_FLOAT, 
        ACCESSOR_TYPE_VECTOR_3, 
        PACKING_FORMAT_FLOAT,
        normals
        )
    }

    mesh_dict = {
        MESH_NAME: tracker_name,
        MESH_PRIMITIVES:[{
            MESH_PRIMITIVE_ATTRIBUTES: accessors,
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0 #TODO: ensure materials are correctly assigned here
        }]
        }

    meshID = len(bucket.data[BUCKET_DATA_MESHES])

    bucket.data[BUCKET_DATA_MESHES].append(mesh_dict)
    bucket.trackers[BUCKET_TRACKER_MESHES][tracker_name] = meshID

    return meshID
    