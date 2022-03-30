import enum
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Core.Managers import AccessorManager, Tracer
from io_advanced_gltf2.Scoops.Mesh.Types import Compound, Primitive, ShapeKeyCompound, ShapeKeyData
from bpy_extras import mesh_utils
from mathutils import Vector
import numpy

def decompose_into_indexed_triangles(mesh, uvIDs, vColorIDs, shapeIDs):
    
    mesh.calc_normals_split()
    mesh.calc_loop_triangles()
    triangles = mesh.loop_triangles

    vertices = mesh.vertices
    loops = mesh.loops
    uvLoops = []
    vcLoops = []
    skData = []

    # array used to store combined vertex and loop data
    compounds = []

    primitives = []
    # create one primitive per material
    for _ in range(len(mesh.materials)):
        primitives.append(Primitive(len(uvIDs), len(vColorIDs), len(shapeIDs)))

    # ensure there is at least one primitive
    if len(primitives) == 0:
        primitives.append(Primitive(len(uvIDs), len(vColorIDs), len(shapeIDs)))


    for uvID in uvIDs:
        uvLoops.append(mesh.uv_layers[uvID].data)
    for vColorID in vColorIDs:
        vcLoops.append(mesh.vertex_colors[vColorID].data)
    for shapeID in shapeIDs:
        skPositions = [] 
        for skp in mesh.shape_keys.key_blocks[shapeID].data: skPositions.append(Util.location_ensure_coord_space(skp.co))
        skRawNormals = []
        for nm in mesh.shape_keys.key_blocks[shapeID].normals_split_get(): skRawNormals.append(nm)
        skNormals = []
        for i in range(0, len(skRawNormals), 3): # for some reason shape key normals get returned as a raw list instead of vectors
            skNormals.append(Util.direction_ensure_coord_space(Vector((skRawNormals[i], skRawNormals[i + 1], skRawNormals[i + 2]))))

        skData.append(ShapeKeyData(skPositions, skNormals, None))

    for i_loop, loop in enumerate(loops):
        position = Util.location_ensure_coord_space(vertices[loop.vertex_index].co)
        normal = Util.direction_ensure_coord_space(loop.normal)
        uv = [None] * len(uvLoops)
        vColor = [None] * len(vcLoops)
        shapeKey = [None] * len(shapeIDs)
        for i in range(len(uv)):
            uv[i] = Util.uv_ensure_coord_space(uvLoops[uvIDs[i]][i_loop].uv)
        for i in range(len(vColor)):
            vColor[i] = vcLoops[vColorIDs[i]][i_loop].color
        for i in range(len(shapeKey)):
            nm = skData[i].normals[i_loop]
            pos = skData[i].positions[loop.vertex_index]
            shapeKey[i] = ShapeKeyCompound(pos, nm, None)
        compounds.append(Compound(position, normal, None, uv, vColor, shapeKey))

    del uvLoops
    del vcLoops
    del skData

    compounds, compoundIndices = numpy.unique(compounds, return_inverse=True)

    for triangle in triangles:
        def add_index(index):
            """
                Checks if new data needs to be written, if not
                automatically add index into the primitive
            """
            if index in p.duplicates:
                p.indices.append(p.duplicates[index])
                return False
            return True

        p = primitives[triangle.material_index]
        for loop_i in triangle.loops:
            loop_i = compoundIndices[loop_i]
            if add_index(loop_i):
                new_i = len(p.positions)
                p.indices.append(new_i)
                p.duplicates[loop_i] = new_i
                compound = compounds[loop_i]
                p.positions.append(compound.position)
                p.normals.append(compound.normal)
                for i, uv in enumerate(compound.uv):
                    p.uv[i].append(uv)
                for i, vc in enumerate(compound.color):
                    p.vertexColor[i].append(vc)
                for i, skc in enumerate(compound.shapeKey):
                    p.shapeKey[i].positions.append(skc.position)
                    p.shapeKey[i].normals.append(skc.normal)
                    p.shapeKey[i].tangents.append(skc.tangent)

    return primitives


def get_accessor_positions(bucket, meshName, depsgraphID, mode, primitive, positions) -> int:

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, MESH_TYPE_TRIANGLES, 0, MESH_ATTRIBUTE_STR_POSITION)
    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, MESH_ATTRIBUTE_STR_POSITION)

    _min = [100000.0, 100000.0, 100000.0]
    _max = [-100000.0, -100000.0, -100000.0]
    for p in positions:
        _min[0] = min(_min[0], p[0])
        _min[1] = min(_min[1], p[1])
        _min[2] = min(_min[2], p[2])

        _max[0] = max(_max[0], p[0])
        _max[1] = max(_max[1], p[1])
        _max[2] = max(_max[2], p[2])

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_3,
    PACKING_FORMAT_FLOAT,
    data=positions,
    tracker=tracker,
    min=_min,
    max=_max,
    name=tracker # TODO: this should not be in release build
    )

def get_accessor_normals(bucket, meshName, depsgraphID, mode, primitive, normals) -> int:

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

def get_accessor_indices(bucket, meshName, depsgraphID, mode, primitive, indices) -> int:

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, mode, primitive, MESH_PRIMITIVE_INDICES.upper())
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

def get_accessor_uv(bucket, meshName, depsgraphID, mode, primitive, uvName, uvs):
    

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, mode, primitive, "UVMAP-" + uvName)
    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, "UVMAP-" + uvName)

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_2,
    PACKING_FORMAT_FLOAT,
    data=uvs,
    tracker=tracker,
    name=tracker # TODO: this should not be in release build
    )

def get_accessor_vertex_color(bucket, meshName, depsgraphID, mode, primitive, vColorName, vColor):

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, mode, primitive, "VCOLOR-" + vColorName)

    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, "VCOLOR-" + vColorName)

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_4,
    PACKING_FORMAT_FLOAT,
    data=vColor,
    tracker=tracker,
    name=tracker # TODO: this should not be in release build
    )