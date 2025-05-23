from io_ggltf import Constants as __c
from io_ggltf.Core import BlenderUtil
import os
from mathutils import Matrix, Vector, Quaternion, Euler
from bpy_extras.io_utils import axis_conversion
import bpy
import re

class ObjectNotFoundException(Exception):
    def __init__(self, objAccessor):
        if type(objAccessor) == tuple:
            print(f"{objAccessor[1]}::{objAccessor[0]} not found within blend file, please check if the library path is correct and linked correctly")
        elif type(objAccessor) == str:
            print(f"{objAccessor} not found within blend file")
        else:
            print(f"Invalid format used while getting object, expected tuple(object name, library) or string, got: {objAccessor}")

class BoneNotFoundException(Exception):
    def __init__(self, accessor):
        self.accessor = accessor

    def __str__(self):
        return f"Bone '{self.accessor[2]}' not found in '{self.accessor[0]}'"

def y_up_matrix(orgMat : Matrix) -> Matrix:
    """
    Multiply the matrix to make it Y+ up
    """
    return get_basis_matrix_conversion() @ orgMat

def y_up_location(orgLoc : Vector) -> Vector:
    """
    Move and flip individual components to match Y+ up coordinate system.
    """
    return Vector((orgLoc[0], orgLoc[2], -orgLoc[1]))

def y_up_rotation(orgRot : Quaternion) -> Quaternion:
    """
    Move and flip individual components to match Y+ up coordinate system.
    Warning: This does not swizzle the order from WXYZ to XYZW.
    """
    return Quaternion((orgRot[0], orgRot[1], orgRot[3], -orgRot[2]))

def y_up_scale(orgScl : Vector) -> Vector:
    """
    Move and flip indivual components to match Y+ up coordinate system
    """
    return Vector((orgScl[0], orgScl[2], orgScl[1]))

def y_up_direction(orgDir: Vector) -> Vector:
    """
    Move and flip individual components to match Y+ up coordinate system.
    """
    return Vector((orgDir[0], orgDir[2], -orgDir[1]))

def correct_uv(orgUV: Vector) -> Vector:
    """
    Move, flip and compensate for difference in V coordinates.
    """
    return Vector((orgUV[0], -orgUV[1] + 1.0))

def bl_math_to_gltf_list(obj):
    """
    Flatten the object into a list.
    For Quaternions: Swizzle the order from WXYZ to XYZW.
    """
    if isinstance(obj, Quaternion):
        return [obj[1], obj[2], obj[3], obj[0]]
    elif isinstance(obj, Matrix):
        l = []
        rows = len(obj)
        cols = len(obj[0])
        for r in range(0, rows):
            for c in range(0, cols):
                l.append(obj[r][c])
        return l
    else:
        return list(obj)

def round_float_list_to_precision(data: list, precision: int):
    """
    Round floats to specified decimal point.
    """
    for i, f in enumerate(data):
        data[i] = round(f, precision)

def cleanup_keys(d: dict):
    to_pop = []
    for k in d.keys():
        #print(f"{k} is of type {type(d[k])}")
        value = d[k]
        if value == None:
            to_pop.append(k)
        elif type(value) == list or type(value) == tuple or type(value) == dict:
            if len(value) == 0:
                to_pop.append(k)
    for p in to_pop:
        d.pop(p)

def get_basis_matrix_conversion():
    convert = axis_conversion(from_forward="-Y", from_up="Z", to_forward="Z", to_up="Y")
    convert.resize_4x4()
    return convert

def try_get_object(accessor):
    try:
        if type(accessor) == str or (type(accessor) == tuple and len(accessor) == 2):
            obj = bpy.data.objects.get(accessor)
            if obj == None:
                raise ObjectNotFoundException(accessor)
            return obj
        else: # in case we get a bone accessor
            obj = bpy.data.objects.get((accessor[0], accessor[1])) # strip the bone name
            if obj == None:
                raise ObjectNotFoundException(accessor)
            return obj

    except Exception as e:
        print(e)
        return None

def try_get_bone(accessor):
    try:
        if type(accessor) == str or (type(accessor) == tuple and len(accessor) == 2):
            return None
        else:
            obj = bpy.data.objects.get((accessor[0], accessor[1]))
            if obj == None:
                return None
            bone = obj.pose.bones[accessor[2]]
            if bone == None:
                return None
            return bone

    except Exception as e:
        return None
    
def name_passes_filters(filter: list[tuple], name: str) -> bool:
    for f in filter:
        #print(f"Filter: {f[0]} | Name: {name} | Whitelist: {f[1]} | Match: {re.search(f[0], name)}")
        match = re.search(f[0], name)
        if f[1] == True: # if its a white list
            if match == None: # and we failed to find a match
                return False 
        else: # if its a blacklist
            if match != None: # and we found a match
                return False
    return True

def name_passes_filter(filter: tuple[str, bool], name:str) -> bool:
    match = re.search(filter[0], name)
    if filter[1] == True: # Whitelist
        if match == None: return False
        else: return True
    else: # Blacklist
        if match != None: return False
        else: return True

def rename_node(bucket, nodeID: int, newName: str):
    node = bucket.data[__c.BUCKET_DATA_NODES][nodeID]
    node[__c.NODE_NAME] = newName

def rename_node(bucket, nodeName: str, newName: str):
    for n in bucket.data[__c.BUCKET_DATA_NODES]:
        if nodeName == n[__c.NODE_NAME]:
            n[__c.NODE_NAME] = newName

def pattern_replace(bucket, dataType: str, pattern: str, newStr: str):
    objects = bucket.data[dataType]
    pattern = re.compile(pattern)
    for obj in objects:
        if __c.__VAR_NAME in obj: # the object here is a dictionary so we check if it has a name first
            name = obj[__c.__VAR_NAME]
            matches = re.findall(pattern, name)
            uniqueMatches = set()
            if len(matches)> 0:
                if type(matches[0]) == tuple:
                    for group in matches:
                        for match in group:
                            if match != "":
                                uniqueMatches.add(match)
                else:
                    for match in matches:
                        uniqueMatches.add(match)

                for unique in uniqueMatches:
                    name = name.replace(unique, newStr)
                obj[__c.__VAR_NAME] = name

def pattern_replace_node_name(bucket, nodeID, pattern: str, newStr: str):
    node = bucket.data[__c.BUCKET_DATA_NODES][nodeID]
    if __c.NODE_NAME in node:
        name = node[__c.NODE_NAME]
        matches = re.findall(pattern, name)
        uniqueMatches = set()
        if len(matches) > 0:
            if type(matches[0]) == tuple:
                for group in matches:
                    for match in group:
                        if match != "":
                            uniqueMatches.add(match)
            else:
                for match in matches:
                    uniqueMatches.add(match)

            
            for unique in uniqueMatches:
                name = name.replace(unique, newStr)
                
            node[__c.NODE_NAME] = name

def pattern_replace_skin_joint_names(bucket, skinID: int, pattern: str, newStr: str):
    skin = bucket.data[__c.BUCKET_DATA_SKINS][skinID]

    if __c.SKIN_JOINTS in skin:
        for joint in skin[__c.SKIN_JOINTS]:
            pattern_replace_node_name(bucket, joint, pattern, newStr)

def create_filter(pattern: str, whitelist: bool):
    return (pattern, whitelist)

def get_all_nodes_in_scene(bucket, sceneID) -> set[int]:
    if not __c.BUCKET_DATA_SCENES in bucket.data or not __c.BUCKET_DATA_NODES in bucket.data:
        return None
    
    nodes = set()
    scene = bucket.data[__c.BUCKET_DATA_SCENES][sceneID]

    if not __c.SCENE_NODES in scene:
        return None

    for nodeID in scene[__c.SCENE_NODES]:
        if nodeID in nodes:
            continue
        hierarchy = get_all_nodes_in_hierarchy(bucket, nodeID)
        nodes.update(hierarchy)
        
    return nodes

def get_all_nodes_in_hierarchy(bucket, topNodeID):
    def add_children(bucket, node: dict, nodes: set):
        if not __c.NODE_CHILDREN in node:
            return
        for c in node[__c.NODE_CHILDREN]:
            add_children(bucket, bucket.data[__c.BUCKET_DATA_NODES][c], nodes)
            nodes.add(c)

    nodes = set()
    node = bucket.data[__c.BUCKET_DATA_NODES][topNodeID]
    nodes.add(topNodeID)

    add_children(bucket, node, nodes)
    return nodes

def get_yup_transforms(childAccessor, parent):
    if parent == None:
        parent = False
    corrected, m = evaluate_matrix(childAccessor, parent)

    if corrected:
        position, rotation, scale = m.decompose()
    else:
        position, rotation, scale = m.decompose()
        position = y_up_location(position)
        rotation = y_up_rotation(rotation)
        scale = y_up_scale(scale)

    return position, rotation, scale

def evaluate_matrix(childAccessor, parent):
    """
    Returns a matrix for the child accessor within parent space.
    
    Args:
        childAccessor (tuple[str, str] or tuple[str, str, str]): Child object accessor
        parent (tuple[str, str], tuple[str, str, str] or bool): When using boolean set to
        True the parent will be found automatically, if False then use world space. If
        If accessor is given then use that object / bone space.

    Returns: tuple[bool, matrix] bool indicates if matrix is Y up
    """

    if type(childAccessor) == str:
        childAccessor = (childAccessor, None)
    if type(parent) == str:
        parent = (parent, None)

    if childAccessor != None and type(parent) == bool:
        childObj = bpy.data.objects.get(childAccessor)
        if parent:
            if childObj.parent_type == __c.BLENDER_TYPE_BONE:
                parent = BlenderUtil.get_parent_accessor(childAccessor)
            else:
                return False, childObj.matrix_local
        else:
            return False, childObj.matrix_world

    if childAccessor != None and type(parent) == tuple:
        childWorldMatrix = get_world_matrix(childAccessor)
        parentWorldMatrix = get_world_matrix(parent)

        return False, parentWorldMatrix.inverted_safe() @ childWorldMatrix
    else:
        if type(parent) == tuple:
            parentWorldMatrix = get_world_matrix(parent)
            return True, parentWorldMatrix.inverted_safe() @ get_basis_matrix_conversion()
        else:
            return True, get_basis_matrix_conversion()

def get_world_matrix(accessor: tuple):
    bone = try_get_bone(accessor)
    obj = try_get_object(accessor)

    if bone != None:
        return obj.matrix_world @ bone.matrix
    else:
        return obj.matrix_world
    
def prep_path(path : str):
    os.makedirs(os.path.dirname(path), exist_ok=True)