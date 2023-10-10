from io_ggltf.Constants import *
from io_ggltf.Core import Util
from io_ggltf.Core.Managers import AccessorManager
from io_ggltf.Core.Scoops.Mesh.Types import *
from bpy_extras import mesh_utils
from mathutils import Vector
import numpy

def decompose_into_indexed_triangles(mesh, vertexGroups, normals, tangents, uvIDs, vColorIDs, shapeIDs, skinDefinition, maxInfluences) -> list:
    """Decompose the mesh into primitives and remove any duplicate vertices based on the other arguments.

    Args:
        mesh (bpy.types.Mesh): Blender mesh data-block.
        vertexGroups (bpy.types.VertexGroups): A collection of vertex groups, extracted from the object.
        normals (bool): Should normals data be included.
        tangets (bool): Should the tangets be calculated.
        uvIDs (list of int): Indices of UV maps that will be added to the mesh.
        vColorIDs (list of int): Indices of vertex colors that will be added to the mesh.
        shapeIDs (list of int): Indices of shape keys that will be added to the mesh.
        skinDefinition (dictionary): A dictionary that is used to determine bone indices and which vertex groups should be included.
        maxInfluences (int): Maximum number of influences, must be multiple of 4, any vertex with less then max influences will be padded with empty data, and any vertex with more then max will only contain highest influences and will be normalised

    Returns:
        list of io_ggltf.Scoops.Mesh.Types.Primitive
    """
    
    if skinDefinition == None:
        maxInfluences = 0 # save memory in case influences is not set 0 already

    influenceDivisions = int(maxInfluences / 4)

    if normals:
        mesh.calc_normals_split()

    if tangents:
        mesh.calc_tangents()
        
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
        primitives.append(Primitive(len(uvIDs), len(vColorIDs), len(shapeIDs), influenceDivisions))

    # ensure there is at least one primitive
    if len(primitives) == 0:
        primitives.append(Primitive(len(uvIDs), len(vColorIDs), len(shapeIDs), influenceDivisions))


    for uvID in uvIDs:
        uvLoops.append(mesh.uv_layers[uvID].data)
    for vColorID in vColorIDs:
        vcLoops.append(mesh.vertex_colors[vColorID].data)
    for shapeID in shapeIDs:
        skPositions = [] 
        for skp in mesh.shape_keys.key_blocks[shapeID].data: skPositions.append(Util.y_up_location(skp.co))
        skRawNormals = []
        for nm in mesh.shape_keys.key_blocks[shapeID].normals_split_get(): skRawNormals.append(nm)
        skNormals = []
        for i in range(0, len(skRawNormals), 3): # for some reason shape key normals get returned as a raw list instead of vectors
            skNormals.append(Util.y_up_direction(Vector((skRawNormals[i], skRawNormals[i + 1], skRawNormals[i + 2]))))

        skData.append(ShapeKeyData(skPositions, skNormals, None))

    for i_loop, loop in enumerate(loops):
        position = Util.y_up_location(vertices[loop.vertex_index].co)
        normal = Util.y_up_direction(loop.normal) if normals else Vector((0.0, 0.0, 0.0))
        if tangents:
            tangent = Util.y_up_direction(loop.tangent)
            tangent = Vector((tangent[0], tangent[1], tangent[2], loop.bitangent_sign))
        else:
            tangent = Vector((0.0, 0.0, 0.0, 0.0))
        boneID, boneInflu = get_vertex_weights(vertices[loop.vertex_index], vertexGroups, skinDefinition, maxInfluences)
        uv = [None] * len(uvLoops)
        vColor = [None] * len(vcLoops)
        shapeKey = [None] * len(shapeIDs)
        for i in range(len(uvLoops)):
            uv[i] = Util.correct_uv(uvLoops[i][i_loop].uv)
        for i in range(len(vcLoops)):
            vColor[i] = vcLoops[i][i_loop].color
        for i in range(len(shapeIDs)):
            nm = skData[i].normals[i_loop]
            pos = skData[i].positions[loop.vertex_index] - position
            shapeKey[i] = ShapeKeyCompound(pos, nm, None)
        compounds.append(Compound(position, normal, tangent, uv, vColor, shapeKey, boneID, boneInflu))

    del uvLoops
    del vcLoops
    del skData
    del vertices
    del loops

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
                p.tangents.append(compound.tangent)
                for division in range(0, influenceDivisions): # vectorize the IDs and influences
                    p.boneID[division].append([compound.boneID[division * 4], compound.boneID[division * 4 + 1], compound.boneID[division * 4 + 2], compound.boneID[division * 4 + 3]])
                    p.boneInfluence[division].append([compound.boneInfluence[division * 4], compound.boneInfluence[division * 4 + 1], compound.boneInfluence[division * 4 + 2], compound.boneInfluence[division * 4 + 3]])

                for i, uv in enumerate(compound.uv):
                    p.uv[i].append(uv)
                for i, vc in enumerate(compound.color):
                    p.vertexColor[i].append(vc)
                for i, skc in enumerate(compound.shapeKey):
                    p.shapeKey[i].positions.append(skc.position)
                    p.shapeKey[i].normals.append(skc.normal)
                    p.shapeKey[i].tangents.append(skc.tangent)
                    
    del compounds
    del compoundIndices
    del triangles

    return primitives


def get_vertex_weights(vertex, vertexGroups, skinDefinition, maxInfleunces):
    """
    Returns array of boneIDs and array of bone influences (normalized), always divisible by 4
    """
    if maxInfleunces <= 0:
        return ([], [])

    vertexWeights = []

    for vertexGroupElement in vertex.groups:
        vertexGroupName = vertexGroups[vertexGroupElement.group].name
        if vertexGroupName in skinDefinition.keys():
            vertexWeights.append((skinDefinition[vertexGroupName], vertexGroupElement.weight))

    if maxInfleunces > len(vertexWeights):
        for _ in range(len(vertexWeights), maxInfleunces):
            vertexWeights.append((0, 0.0)) # insert empty data if there isn't enough to match the influence count

    vertexWeights.sort(key=lambda k: k[1], reverse=True) # sort by weight, highest -> lowest
    vertexWeights = vertexWeights[:maxInfleunces] # slice list to ensure it is divisable by 4

    # convert both to arrays since thats how they will be stored by the primitives, tuples were just for easier sorting
    boneID = []
    boneInflu = []
    for bf in vertexWeights:
        boneID.append(bf[0])
        boneInflu.append(bf[1])

    # ensure that total weight of all influences is 1.0 (or as close to it as float allows *shrug*)
    normalizer = sum(boneInflu)
    if normalizer != 0.0:
        normalizer = 1.0 / normalizer
        for i, b in enumerate(boneInflu):
            boneInflu[i] = b * normalizer
    else:
        boneInflu[0] = 1.0

    return boneID, boneInflu



def get_accessor_positions(bucket, positions) -> int:

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
    min=_min,
    max=_max,
    )

def get_accessor_normals(bucket, normals) -> int:

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_3,
    PACKING_FORMAT_FLOAT,
    data=normals
    )

def get_accessor_indices(bucket, indices) -> int:

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_UNSIGNED_INT,
    ACCESSOR_TYPE_SCALAR,
    PACKING_FORMAT_U_INT,
    data=indices
    )

def get_accessor_uv(bucket, uvs):
    
    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_2,
    PACKING_FORMAT_FLOAT,
    data=uvs
    )

def get_accessor_vertex_color(bucket, vColor):

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_4,
    PACKING_FORMAT_FLOAT,
    data=vColor
    )

def get_accessor_tangents(bucket, tangents):

    return AccessorManager.add_accessor(bucket,
    ACCESSOR_COMPONENT_TYPE_FLOAT,
    ACCESSOR_TYPE_VECTOR_4,
    PACKING_FORMAT_FLOAT,
    data=tangents
    )