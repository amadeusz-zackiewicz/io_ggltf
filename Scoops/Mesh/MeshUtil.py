import enum
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Core.Managers import AccessorManager, Tracer
from io_advanced_gltf2.Scoops.Mesh.Types import Compound, Primitive
from bpy_extras import mesh_utils
import numpy

def decompose_into_indexed_triangles(mesh, uvIDs, vColorIDs, shapeIDs):
    
    mesh.calc_normals_split()
    mesh.calc_loop_triangles()
    triangles = mesh.loop_triangles

    vertices = mesh.vertices
    loops = mesh.loops
    uvLoops = []
    vcLoops = []

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
    

    for i_loop, loop in enumerate(loops):
        position = Util.location_ensure_coord_space(vertices[loop.vertex_index].co)
        normal = Util.direction_ensure_coord_space(loop.normal)
        uv = [None] * len(uvLoops)
        vColor = [None] * len(vcLoops)
        for i in range(len(uv)):
            uv[i] = Util.uv_ensure_coord_space(uvLoops[uvIDs[i]][i_loop].uv)
        for i in range(len(vColor)):
            vColor[i] = vcLoops[vColorIDs[i]][i_loop].color

        compounds.append(Compound(position, normal, None, uv, vColor, None))

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
        print(p)
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

    return primitives


def get_accessor_positions(bucket, meshName, depsgraphID, mode, primitive, positions, min, max) -> int:

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

def get_accessor_uv(bucket, meshName, depsgraphID, mode, primitive, uv_name, uvs):
    

    id = Tracer.trace_mesh_attribute_id(bucket, meshName, depsgraphID, mode, primitive, uv_name)
    if id != None:
        return id

    tracker = Tracer.make_mesh_attribute_tracker(meshName, depsgraphID, mode, primitive, uv_name)

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_2,
    PACKING_FORMAT_FLOAT,
    data=uvs,
    tracker=tracker,
    name=tracker # TODO: this should not be in release build
    )