from ctypes import util
import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Core.Scoops import Node
from mathutils import Matrix, Vector
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Managers import AccessorManager

def reserve_bone_ids(bucket: Bucket, objAccessors, blacklist = set()) -> int:
    def bone_counter(bone, blacklist, boneCount):
        if bone.name in blacklist:
            return
        
        for c in bone.children:
            bone_counter(c, blacklist, boneCount)
        
        boneCount[0] += 1

    objects = [bpy.data.objects.get(o) for o in objAccessors]
    bones = []
    rootBones = []
    boneCount = [0] # just so i can pass it as reference, im lazy

    for obj in objects:
        bones.extend([b for b in obj.pose.bones])

    for i, bone in enumerate(bones):
        if bone.parent == None:
            rootBones.append(i)

    for r in rootBones:
        bone_counter(bones[r], blacklist, boneCount)

    nodeIDOffset = bucket.preScoopCounts[BUCKET_DATA_NODES]
    bucket.preScoopCounts[BUCKET_DATA_NODES] = nodeIDOffset + boneCount[0]

    return nodeIDOffset

    

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

def scoop_skin(bucket: Bucket, objAccessors: tuple, getInversedBinds = False, blacklist = set(), mainArmature = 0, nodeIDOffset = 0, skinID = 0):

    objects = [bpy.data.objects.get(o) for o in objAccessors]
    bones = []

    for obj in objects:
        bones.extend([(b, obj.matrix_world) for b in obj.pose.bones])
    skinDefinition = {}
    jointTree = []
    rootBones = []
    rootNodes = []
    skeleton = []
    joints = []

    skinDict = {}
    skinDict[SKIN_NAME] = objects[0].name

    for i, b in enumerate(bones):
        bone = b[0]
        skinDefinition[bone.name] = i
        if not bone.parent:
            rootBones.append(i)

    for root in rootBones:
        bone = bones[root][0]
        objWorldMatrix = bones[root][1]
        __get_joint_hierarchy(bone, None, blacklist, jointTree, objWorldMatrix)

    jointCounter = [0] # temporary
    for rootJoint in jointTree:
        __get_joint_nodeIDs(rootJoint, nodeIDoffset=nodeIDOffset, jointCounter=jointCounter)
        __calculate_local_matrices(rootJoint, objects[mainArmature].matrix_world.inverted_safe())
        __joint_hierarchy_to_nodes(bucket, rootJoint)
        __get_joint_list(rootJoint, joints)
        __get_joint_dictionary(rootJoint, skinDefinition)
        rootNodes.append(rootJoint.nodeID)
        skeleton.append(rootJoint.jointID)
    del jointCounter

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
        data=inversedBinds
        )
    
    bucket.data[BUCKET_DATA_SKINS][skinID] = skinDict
    bucket.skinDefinition[skinID] = (skinDefinition)

    return rootNodes

def __get_joint_nodeIDs(joint: Joint, nodeIDoffset: int, jointCounter=[0]):
    def get_ids(joint: Joint, nodeIDoffset: int, jointCounter: list):
        for c in joint.children:
            get_ids(c, nodeIDoffset, jointCounter)

        joint.nodeID = nodeIDoffset + jointCounter[0]
        jointCounter[0] += 1

    get_ids(joint, nodeIDoffset, jointCounter)

def __get_joint_hierarchy(bone, parentJoint, blacklist, jointTree, objWorldMatrix):
    if bone.name in blacklist:
        return

    joint = Joint()
    joint.name = bone.name
    joint.blenderBone = bone
    joint.worldMatrix = Util.y_up_matrix(objWorldMatrix @ bone.matrix)

    for c in bone.children:
        cJoint = __get_joint_hierarchy(c, joint, blacklist, jointTree, objWorldMatrix)
        if cJoint != None:
            joint.children.append(cJoint)

    # root joint
    if parentJoint == None:
        jointTree.append(joint)
    else:
        joint.parent = parentJoint

    return joint

def __calculate_local_matrices(joint: Joint, objectWorldMatrixInverse):
    if joint.parent == None:
        joint.localMatrix = objectWorldMatrixInverse @ joint.worldMatrix
    else:
        joint.localMatrix = joint.parent.worldMatrix.inverted_safe() @ joint.worldMatrix
    for c in joint.children:
        __calculate_local_matrices(c, objectWorldMatrixInverse)

def __joint_hierarchy_to_nodes(bucket: Bucket, joint: Joint):
    def recursive_to_nodes(bucket: Bucket, joint: Joint):
        children = []
        for c in joint.children:
            children.append(recursive_to_nodes(bucket, c))

        loc, rot, sc = joint.localMatrix.decompose()
        node = Node.obj_to_node(
            name=joint.name,
            translation=loc,
            rotation=rot,
            scale=sc,
            children=children
        )

        bucket.data[BUCKET_DATA_NODES][joint.nodeID] = node

        return joint.nodeID

    recursive_to_nodes(bucket, joint)
    
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
        __calculate_inverse_binds(c, objWorldMatrix)

    joint.inverseBind = Util.y_up_matrix(objWorldMatrix @ joint.blenderBone.bone.matrix_local).inverted_safe()
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
