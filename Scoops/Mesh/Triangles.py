from math import ceil
from io_advanced_gltf2.Core.Managers import AccessorManager
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Managers import Tracer
from io_advanced_gltf2.Scoops.Mesh import MeshUtil
from io_advanced_gltf2.Core.Bucket import Bucket
from mathutils import Vector

def scoop_indexed(bucket: Bucket, meshObj, vertexGroups, uvMaps, vertexColors, shapeKeys, tangents, skinID, maxInfluences = 4):
    """_summary_

    Args:
        bucket (Bucket)
        meshObj (bpy.types.Mesh): Evaluated Blender mesh data-block
        vertexGroups (bpy.types.VertexGroups): Vertex group extracted from the object that holds the mesh
        uvMaps (list of string): Names of UV maps that will be added to the mesh data.
        vertexColors (_type_): Names of vertex colors that will be added to the mesh data.
        shapeKeys (_type_): Names of shape keys that will be added to the mesh data.
        tangents (_type_): Should the tangent data be included.
        skinID (_type_): ID of the skin to be used when gathering bones, provide None if not needed.
        maxInfluences (int, optional): Maximum amount of bone influences, will be rounded up to the closest multiple of 4, ignored when skinID is None. Defaults to 4.

    Returns:
        tuple: a tuple containing index of the mesh and shape key weights (None if no shape key data is included)
    """

    originalName = meshObj.original.name
    depsID = id(meshObj)

    if skinID != None:
        if maxInfluences % 4 != 0: # check if the influence count is a multiple of 4
            newInfCount = int(ceil((maxInfluences / 4) * 4))
            print("Bone Influences must be multiples of 4, and have been adjusted from:", maxInfluences, "to:", newInfCount)
            maxInfluences = newInfCount

    tracker = Tracer.make_mesh_tracker(originalName, depsID, MESH_TYPE_TRIANGLES, uvMaps, vertexColors, shapeKeys, tangents, skinID)

    print("---------------------",originalName)

    if tracker in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][tracker]

    uvIDs = []
    vColorIDs = []
    shapeKeyIDs = []

    # convert UV map names into indices
    for uvName in uvMaps: 
        if uvName in meshObj.uv_layers:
            for i, uvLayer in enumerate(meshObj.uv_layers):
                if uvName == uvLayer.name:
                    uvIDs.append(i)
                    break
        else:
            print(uvName, " UV map not found inside ", originalName, " and will be ignored")

    # convert vertex color names into indices
    for vColorName in vertexColors: 
        if vColorName in meshObj.vertex_colors:
            for i, vColorLayer in enumerate(meshObj.vertex_colors):
                if vColorName == vColorLayer.name:
                    vColorIDs.append(i)
        else:
            print(vColorName, " Vertex Color not found inside ", originalName, " and will be ignored")

    # convert shape key names into indices
    for shapeKeyName in shapeKeys: 
        if shapeKeyName in meshObj.shape_keys.key_blocks:
            for i, sk in enumerate(meshObj.shape_keys.key_blocks):
                if shapeKeyName == sk.name:
                    shapeKeyIDs.append(i)
        else:
            print(shapeKeyName, "Shape Key not found inside", originalName, "and will be ignored")

    # get the skin definition (a dictionary of [BoneName : NodeID])
    skinDef = None if skinID == None else bucket.skinDefinition[skinID] 
    primitives = MeshUtil.decompose_into_indexed_triangles(meshObj, vertexGroups, uvIDs, vColorIDs, shapeKeyIDs, skinDef, maxInfluences)

    # prepare the dictionary object
    meshDict = {
        MESH_NAME: tracker,
        MESH_PRIMITIVES: []
        }

    # merge each primitive into the binary blob and add accessors into the dictionary
    for i, p in enumerate(primitives): 
        # prepare the dictionary for this primitive
        primitiveDict = { 
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES,
            MESH_PRIMITIVE_MATERIAL: 0, # TODO: materials are not yet supported
            }

        positionsAccessor = MeshUtil.get_accessor_positions(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, p.positions)
        normalsAccessor = MeshUtil.get_accessor_normals(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, p.normals) # TODO: normals should be optional
        indicesAccessor = MeshUtil.get_accessor_indices(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, p.indices)

        primitiveDict[MESH_PRIMITIVE_INDICES] = indicesAccessor
        primitiveDict[MESH_PRIMITIVE_ATTRIBUTES] = {
            MESH_ATTRIBUTE_STR_POSITION: positionsAccessor,
            MESH_ATTRIBUTE_STR_NORMAL: normalsAccessor,
        }

        # bone influence data
        if skinID != None: 
            for division in range(int(maxInfluences / 4)):

                jointAccessor = AccessorManager.add_accessor(bucket, 
                componentType=ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT, type=ACCESSOR_TYPE_VECTOR_4, 
                packingFormat=PACKING_FORMAT_U_SHORT, data=p.boneID[division], tracker=None)

                weightsAccessor = AccessorManager.add_accessor(bucket,
                componentType=ACCESSOR_COMPONENT_TYPE_FLOAT, type=ACCESSOR_TYPE_VECTOR_4,
                packingFormat=PACKING_FORMAT_FLOAT, data=p.boneInfluence[division], tracker=None)

                primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_JOINT + str(division)] = jointAccessor
                primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_WEIGHT + str(division)] = weightsAccessor

        # UV data
        for i_uv, uvID in enumerate(uvIDs): 
            uvAccessor = MeshUtil.get_accessor_uv(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, meshObj.uv_layers[uvID].name, p.uv[i_uv])
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_TEXCOORD + str(i_uv)] = uvAccessor
            
        # vertex color data
        for i_vc, vcID in enumerate(vColorIDs): 
            vColorAccessor = MeshUtil.get_accessor_vertex_color(bucket, originalName, depsID, MESH_TYPE_TRIANGLES, i, meshObj.vertex_colors[vcID].name, p.vertexColor[i_vc])
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_COLOR + str(i_vc)] = vColorAccessor

        # shape key data
        targets = []
        for i_sk, skID in enumerate(shapeKeyIDs):
            morph = {}
            morphName = originalName + "//" + meshObj.shape_keys.key_blocks[skID].name
            print(__file__, "79 --", len(meshObj.loops), len(p.shapeKey[i_sk].positions))
            skPosAccessor = MeshUtil.get_accessor_positions(bucket, morphName, depsID, MESH_TYPE_TRIANGLES, i, p.shapeKey[i_sk].positions)
            skNmAccessor = MeshUtil.get_accessor_normals(bucket, morphName, depsID, MESH_TYPE_TRIANGLES, i, p.shapeKey[i_sk].normals)
            morph[MESH_ATTRIBUTE_STR_POSITION] = skPosAccessor
            morph[MESH_ATTRIBUTE_STR_NORMAL] = skNmAccessor # TODO: shape key normals should be optional
            targets.append(morph)

        if len(targets) > 0:
            primitiveDict[MESH_PRIMITIVE_TARGETS] = targets

        meshDict[MESH_PRIMITIVES].append(primitiveDict)

    if len(shapeKeyIDs) > 0:
        weights = [0.0] * len(shapeKeyIDs)

        #for i_sk, skID in enumerate(shapeKeyIDs):
            #weights[i_sk] = meshObj.shape_keys.key_blocks[skID].value # TODO: add setting to decide if weights should be zero or same as in blender

        meshDict[MESH_WEIGHTS] = weights

    

    meshID = len(bucket.data[BUCKET_DATA_MESHES])

    bucket.data[BUCKET_DATA_MESHES].append(meshDict)
    bucket.trackers[BUCKET_TRACKER_MESHES][tracker] = meshID

    return (meshID, None, None) # TODO: the return info should be just meshID and weights, update everything upwards