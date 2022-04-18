from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Scoops import Node
from mathutils import Matrix
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Managers import AccessorManager

def scoop_skin(bucket: Bucket, obj, getInversedBinds = False, blacklist = set()):

    bones = obj.pose.bones
    nameToID = {}
    rootBones = []
    includeBone = [True] * len(bones)
    calculatedMatrices = []
    inversedBinds = []

    # find root bone IDs and create dictionary to get bone indices by name
    for i, b in enumerate(bones):
        nameToID[b.name] = i
        if not b.parent:
            rootBones.append(i)

    # mark bones for exclusion based on blacklist and hierarchy
    for boneID in rootBones:
        __recursive_get_exclusions(bones[boneID], includeBone, nameToID, blacklist)

    for i, b in enumerate(bones):
        if includeBone[i]:
            matrix = None
            if b.parent:
                correction_matrix = b.parent.bone.matrix_local.inverted_safe() @ b.bone.matrix_local
                matrix_basis = b.parent.bone.matrix_local.inverted_safe() @ b.bone.matrix_local
                matrix_basis = matrix_basis.inverted_safe() @ b.parent.matrix.inverted_safe() @ b.matrix
                matrix = correction_matrix @ matrix_basis
            else:
                correction_matrix = Util.get_basis_matrix_conversion() @ b.bone.matrix_local
                matrix_basis = b.matrix
                matrix_basis = obj.convert_space(pose_bone=b, matrix=matrix_basis, from_space="POSE", to_space="LOCAL")
                matrix = correction_matrix @ matrix_basis

            calculatedMatrices.append(matrix)
            inversedBinds.append(Util.matrix_ensure_coord_space(b.bone.matrix_local.inverted_safe()))
        else:
            calculatedMatrices.append(None)
            inversedBinds.append(None)

    rootNodes, allNodes, skinDefinition = __bones_to_nodes(bucket, bones, rootBones, includeBone, nameToID, calculatedMatrices)
    
    skinDict = {SKIN_JOINTS: allNodes}

    if len(rootNodes) == 1:
        skinDict[SKIN_SKELETON] = rootNodes[0]

    if getInversedBinds:
        for i in range(len(inversedBinds), 0, -1):
            if inversedBinds[i] == None:
                inversedBinds.pop(i)

        iBindID = AccessorManager.add_accessor(bucket,
        componentType=ACCESSOR_COMPONENT_TYPE_FLOAT,
        type=ACCESSOR_TYPE_MATRIX_4,
        packingFormat=PACKING_FORMAT_FLOAT,
        data=inversedBinds,
        name=obj.name + "-Skin-Inverse-Binds" # TODO: remove after testing is finished
        )

        skinDict[SKIN_INVERSE_BIND_MATRICES] = iBindID

    skinID = len(bucket.data[BUCKET_DATA_SKINS])
    bucket.data[BUCKET_DATA_SKINS].append(skinDict)
    bucket.skinDefinition.append(skinDefinition)

    return skinID

def __bones_to_nodes(bucket, bones, rootBonesID, includeBone, nameToID, calculatedMatrices):
    nodeIDs = []
    rootNodeIDs = []
    definition = {} # a dictionary of name : bone index, this is for mesh bone influences

    for rootBoneID in rootBonesID:
        if includeBone[rootBoneID]:
            nodeID, childrenIDs, childDefinitions = __recursive_bones_to_nodes(bucket, rootBoneID, bones, includeBone, nameToID, calculatedMatrices)
            if nodeID != None:
                rootNodeIDs.append(nodeID)
            nodeIDs.extend(childrenIDs)
            for key in childDefinitions:
                definition[key] = childDefinitions[key]

    return (rootNodeIDs, nodeIDs, definition)
            

def __recursive_bones_to_nodes(bucket, boneID, bones, includeBone, nameToID, calculatedMatrices):
    nodeIDs = []
    definition = {}
    nodeChildren = []

    bone = bones[boneID]

    for c in bone.children:
        childID = nameToID[c.name]
        if includeBone[childID]:
            childNodeID, childNodeIDs, childrenDef = __recursive_bones_to_nodes(bucket, childID, bones, includeBone, nameToID, calculatedMatrices)
            if childNodeID != None:
                nodeChildren.append(childNodeID)
            nodeIDs.extend(childNodeIDs)
            for ck in childrenDef.keys():
                definition[ck] = childrenDef[ck]

    nodeID = __bone_to_node(bucket, bone, calculatedMatrices[boneID], nodeChildren)

    definition[bone.name] = len(nodeIDs)
    nodeIDs.append(nodeID)

    return nodeID, nodeIDs,definition

def __bone_to_node(bucket, bone, matrix, children):

    loc, rot, sc = matrix.decompose()
    return Node.__obj_to_node(bucket, name=bone.name, 
    translation=loc, 
    rotation=rot, 
    scale=sc,
    children=children)

def __recursive_get_exclusions(bone, includeBone, nameToID, blacklist):
    boneID = nameToID[bone.name]

    if bone.parent:
        if not includeBone[nameToID[bone.parent.name]]:
            includeBone[boneID] = False
    if bone.name in blacklist:
        includeBone[boneID] = False

    for c in bone.children:
        __recursive_get_exclusions(c, includeBone, nameToID, blacklist)
