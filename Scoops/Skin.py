from ctypes import util
import enum
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Scoops import Node
from mathutils import Matrix, Vector
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Managers import AccessorManager

class Joint:
    def __init__(self):
        self.name = ""
        self.blenderBone = None
        self.children = []
        self.parent = None
        self.localMatrix = None
        self.worldMatrix = None
        self.inverseBind = None
        self.nodeID = -1
        self.jointID = -1

def scoop_skin(bucket: Bucket, obj, getInversedBinds = False, blacklist = set()):
    bones = obj.pose.bones
    skinDefinition = {}
    jointTree = []
    rootBones = []
    rootNodes = []
    nodeIDs = []
    skeleton = []
    joints = []

    skinDict = {}

    for i, b in enumerate(bones):
        skinDefinition[b.name] = i
        if not b.parent:
            rootBones.append(i)

    for root in rootBones:
        __get_joint_hierarchy(bones[root], None, blacklist, jointTree, obj.matrix_world)

    for rootJoint in jointTree:
        __calculate_local_matrices(rootJoint, obj.matrix_world.inverted_safe())
        __joint_hierarchy_to_nodes(bucket, rootJoint, nodeIDs)
        __get_joint_list(rootJoint, joints)
        __get_joint_dictionary(rootJoint, skinDefinition)
        rootNodes.append(rootJoint.nodeID)
        skeleton.append(rootJoint.jointID)

    skinDict[SKIN_JOINTS] = joints

    if len(skeleton) == 1:
        skinDict[SKIN_SKELETON] = skeleton[0]

    if getInversedBinds:
        inversedBinds = []
        for rootJoint in jointTree:
            __calculate_inverse_binds(rootJoint, obj.matrix_world)
            __inverse_binds_to_list(rootJoint, inversedBinds)

        skinDict[SKIN_INVERSE_BIND_MATRICES] = AccessorManager.add_accessor(bucket,
        componentType=ACCESSOR_COMPONENT_TYPE_FLOAT,
        type=ACCESSOR_TYPE_MATRIX_4,
        packingFormat=PACKING_FORMAT_FLOAT,
        data=inversedBinds,
        name=obj.name + "-Skin-Inverse-Binds", # TODO: remove after testing is finished
        tracker=obj.name + "-Skin-Inverse-Binds"
        )

    skinID = len(bucket.data[BUCKET_DATA_SKINS])
    bucket.data[BUCKET_DATA_SKINS].append(skinDict)
    bucket.skinDefinition.append(skinDefinition)

    return skinID, rootNodes

def __get_joint_hierarchy(bone, parentJoint, blacklist, jointTree, objWorldMatrix):
    if bone.name in blacklist:
        return

    joint = Joint()
    joint.name = bone.name
    joint.blenderBone = bone
    joint.worldMatrix = Util.matrix_ensure_coord_space(objWorldMatrix @ bone.matrix)

    for c in bone.children:
        cJoint = __get_joint_hierarchy(c, parentJoint, blacklist, jointTree, objWorldMatrix)
        if cJoint != None:
            joint.children.append(cJoint)

    # root joint
    if parentJoint == None:
        jointTree.append(joint)
    else:
        joint.parent = parentJoint

def __calculate_local_matrices(joint: Joint, objectWorldMatrixInverse):
    if joint.parent == None:
        joint.localMatrix = objectWorldMatrixInverse @ joint.worldMatrix
    else:
        joint.localMatrix = joint.parent.inversed_safe() @ joint.worldMatrix
    for c in joint.children:
        __calculate_local_matrices(c, objectWorldMatrixInverse)

def __joint_hierarchy_to_nodes(bucket, joint: Joint, nodeIDs):
    children = []
    for c in joint.children:
        childNodeID = __joint_hierarchy_to_nodes(c)
        nodeIDs.append(childNodeID)

    loc, rot, sc = joint.localMatrix.decompose()
    nodeID = Node.__obj_to_node(bucket, 
    name=joint.name, 
    translation=loc, 
    rotation=rot, 
    scale=sc,
    children=children)

    joint.nodeID = nodeID
    nodeIDs.append(nodeID)
    return nodeID
    
def __get_joint_dictionary(joint: Joint, nameToID: dict):
    for c in joint.children:
        __get_joint_dictionary(c, nameToID)

    nameToID[joint.name] = joint.jointID

def __get_joint_list(joint: Joint, joints):
    for c in joint.children:
        __get_joint_list(c, joints)

    joint.jointID = len(joints)
    joints.append(joint.nodeID)

def __calculate_inverse_binds(joint: Joint, objWorldMatrix):
    for c in joint.children:
        __calculate_inverse_binds(c)

    joint.inverseBind = Util.matrix_ensure_coord_space(objWorldMatrix @ joint.blenderBone.bone.matrix_local).inverted_safe()
    # I spend 3 days trying to figure out what I'm doing wrong and gave up
    # I have absolutely no idea why I have to do this
    # I even tried copying code from the official blender exporter and it still produced wrong results
    # Maybe I missed something
    # so it is what it is
    joint.inverseBind[3][0] = joint.inverseBind[0][3]
    joint.inverseBind[3][1] = joint.inverseBind[1][3]
    joint.inverseBind[3][2] = joint.inverseBind[2][3]

    joint.inverseBind[0][3] = 0.0
    joint.inverseBind[1][3] = 0.0
    joint.inverseBind[2][3] = 0.0

def __inverse_binds_to_list(joint: Joint, binds):
    for c in joint.children:
        __inverse_binds_to_list(c, binds)

    binds.append(joint.inverseBind)
