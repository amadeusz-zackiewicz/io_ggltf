from math import ceil
from io_ggltf.Core.Managers import AccessorManager
from io_ggltf.Constants import *
from io_ggltf.Core.Scoops.Mesh import MeshUtil
from io_ggltf.Core.Bucket import Bucket
from mathutils import Vector
from io_ggltf.Core import Util

def scoop_indexed_and_merge(bucket: Bucket, meshObjects, meshWorldMatrix, name, targetWorldMatrix, normals, vertexGroups, uvMaps, vertexColors, shapeKeys, shapeKeyNormals, tangents, skinID, assignedID, maxInfluences = 4):
    
    if skinID != None:
        if maxInfluences % 4 != 0: # check if the influence count is a multiple of 4
            newInfCount = int(ceil((maxInfluences / 4) * 4))
            print("Bone Influences must be multiples of 4, and have been adjusted from:", maxInfluences, "to:", newInfCount)
            maxInfluences = newInfCount

    mappedMeshes = []
    allMatNames = set()
    combinedPrimitives = []
    noMatPrimitive = None

    for meshIndex, meshObj in enumerate(meshObjects):
        transformShapeKeys = True if len(shapeKeys) > 0 else False
        meshObj.transform(meshWorldMatrix[meshIndex], shape_keys=transformShapeKeys)
        meshObj.transform(targetWorldMatrix.inverted_safe(), shape_keys=transformShapeKeys)
        meshObj.update()

        uvIDs = []
        vColorIDs = []
        shapeKeyIDs = []
        materialNames = []

        for i, material in enumerate(meshObj.materials):
            if material == None:
                tempMatName = f"::TEMP::{meshObj.name}__{i}"
                materialNames.append(tempMatName)
                allMatNames.add(tempMatName)
            else:
                materialNames.append(material.name)
                allMatNames.add(material.name)

        # convert UV map names into indices
        for uvName in uvMaps: 
            if uvName in meshObj.uv_layers:
                for i, uvLayer in enumerate(meshObj.uv_layers):
                    if uvName == uvLayer.name:
                        uvIDs.append(i)
                        break
            else:
                raise Exception(f" UV map '{uvName}' not found inside {meshObj.name}.")

        # convert vertex color names into indices
        for vColorName in vertexColors: 
            if vColorName in meshObj.vertex_colors:
                for i, vColorLayer in enumerate(meshObj.vertex_colors):
                    if vColorName == vColorLayer.name:
                        vColorIDs.append(i)
            else:
                raise Exception(f"Vertex Color '{vColorName}' not found inside {meshObj.name}.")

        # convert shape key names into indices
        for shapeKeyName in shapeKeys: 
            if shapeKeyName in meshObj.shape_keys.key_blocks:
                for i, sk in enumerate(meshObj.shape_keys.key_blocks):
                    if shapeKeyName == sk.name:
                        shapeKeyIDs.append(i)
            else:
                raise Exception(f"Shape Key '{shapeKeyName}' not found inside {meshObj.name}.")

        # get the skin definition (a dictionary of [BoneName : NodeID])
        skinDef = None if skinID == None else bucket.skinDefinition[skinID]
        primitives = MeshUtil.decompose_into_indexed_triangles(meshObj, vertexGroups[meshIndex], normals, tangents, uvIDs, vColorIDs, shapeKeyIDs, skinDef, maxInfluences)

        if len(materialNames) > 0:
            primitiveMapping = {}
            for meshIndex, p in enumerate(primitives):
                if len(p.positions) > 0:
                    primitiveMapping[materialNames[meshIndex]] = p
            mappedMeshes.append(primitiveMapping)
        else:
            for p in primitives:
                if noMatPrimitive == None:
                    noMatPrimitive = p
                else:
                    noMatPrimitive.extend(p)


    for matName in allMatNames:
        matchingPrimitives = []
        for decMesh in mappedMeshes:
            if matName in decMesh:
                matchingPrimitives.append(decMesh[matName])

        if len(matchingPrimitives) > 0:
            for p in matchingPrimitives[1:]:
                matchingPrimitives[0].extend(p)

            combinedPrimitives.append(matchingPrimitives[0])
    if noMatPrimitive != None:
        combinedPrimitives.append(noMatPrimitive)

    del mappedMeshes
    
    __write_mesh(bucket=bucket, meshName=name, primitives=combinedPrimitives, normals=normals, tangents=tangents, skinID=skinID, maxInfluences=maxInfluences, uvCount=len(combinedPrimitives[0].uv), vColorCount=len(combinedPrimitives[0].vertexColor), shapeKeyCount=len(combinedPrimitives[0].shapeKey), assignedID=assignedID, shapeKeyWeights=[0.0 for key in combinedPrimitives[0].shapeKey], shapeKeyNormals=shapeKeyNormals)

def __write_mesh(bucket, meshName, primitives, 
normals: bool, 
tangents: bool, 
skinID: int, 
maxInfluences: int, 
uvCount: int, 
vColorCount: int, 
shapeKeyCount: int, 
shapeKeyNormals: bool, 
shapeKeyWeights: list[float], 
assignedID: int
):

    # prepare the dictionary object
    meshDict = {
        MESH_NAME: meshName,
        MESH_PRIMITIVES: []
        }

    # merge each primitive into the binary blob and add accessors into the dictionary
    for p in primitives:
        # prepare the dictionary for this primitive
        primitiveDict = { 
            MESH_PRIMITIVE_MODE: MESH_TYPE_TRIANGLES
            }

        positionsAccessor = MeshUtil.get_accessor_positions(bucket, p.positions)
        indicesAccessor = MeshUtil.get_accessor_indices(bucket, p.indices)

        primitiveDict[MESH_PRIMITIVE_INDICES] = indicesAccessor
        primitiveDict[MESH_PRIMITIVE_ATTRIBUTES] = { MESH_ATTRIBUTE_STR_POSITION: positionsAccessor }
        if normals:
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_NORMAL] = MeshUtil.get_accessor_normals(bucket, p.normals)
        if tangents:
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_TANGENT] = MeshUtil.get_accessor_tangents(bucket, p.tangents)

        # bone influence data
        if skinID != None: 
            for division in range(int(maxInfluences / 4)):

                jointAccessor = AccessorManager.add_accessor(bucket, 
                componentType=ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT, type=ACCESSOR_TYPE_VECTOR_4, 
                packingFormat=PACKING_FORMAT_U_SHORT, data=p.boneID[division])

                weightsAccessor = AccessorManager.add_accessor(bucket,
                componentType=ACCESSOR_COMPONENT_TYPE_FLOAT, type=ACCESSOR_TYPE_VECTOR_4,
                packingFormat=PACKING_FORMAT_FLOAT, data=p.boneInfluence[division])

                primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_JOINT + str(division)] = jointAccessor
                primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_WEIGHT + str(division)] = weightsAccessor

        # UV data
        for i_uv in range(uvCount): 
            uvAccessor = MeshUtil.get_accessor_uv(bucket, p.uv[i_uv])
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_TEXCOORD + str(i_uv)] = uvAccessor
            
        # vertex color data
        for i_vc in range(vColorCount): 
            vColorAccessor = MeshUtil.get_accessor_vertex_color(bucket, p.vertexColor[i_vc])
            primitiveDict[MESH_PRIMITIVE_ATTRIBUTES][MESH_ATTRIBUTE_STR_COLOR + str(i_vc)] = vColorAccessor

        # shape key data
        targets = []
        for i_sk in range(shapeKeyCount):
            morph = {}
            skPosAccessor = MeshUtil.get_accessor_positions(bucket, p.shapeKey[i_sk].positions)
            morph[MESH_ATTRIBUTE_STR_POSITION] = skPosAccessor
            if shapeKeyNormals:
                skNmAccessor = MeshUtil.get_accessor_normals(bucket, p.shapeKey[i_sk].normals)
                morph[MESH_ATTRIBUTE_STR_NORMAL] = skNmAccessor
            targets.append(morph)

        if len(targets) > 0:
            primitiveDict[MESH_PRIMITIVE_TARGETS] = targets

        meshDict[MESH_PRIMITIVES].append(primitiveDict)

        #for i_sk, skID in enumerate(shapeKeyIDs):
            #weights[i_sk] = meshObj.shape_keys.key_blocks[skID].value # TODO: add setting to decide if weights should be zero or same as in blender

        #meshDict[MESH_WEIGHTS] = weights


    bucket.data[BUCKET_DATA_MESHES][assignedID] = meshDict