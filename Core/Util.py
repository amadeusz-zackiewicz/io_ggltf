from io_ggltf import Keywords as __k
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

def y_up_matrix(org_mat : Matrix) -> Matrix:
    return get_basis_matrix_conversion() @ org_mat

def y_up_location(org_loc : Vector) -> Vector:
    return Vector((org_loc[0], org_loc[2], -org_loc[1]))


def y_up_rotation(org_rot : Quaternion) -> Quaternion:
    return Quaternion((org_rot[0], org_rot[1], org_rot[3], -org_rot[2]))


def y_up_scale(org_scl : Vector) -> Vector:
    return Vector((org_scl[0], org_scl[2], org_scl[1]))


def y_up_direction(org_dir: Vector) -> Vector:
    return Vector((org_dir[0], org_dir[2], -org_dir[1]))

def correct_uv(org_uv: Vector) -> Vector:
    return Vector((org_uv[0], 1 - org_uv[1]))

def bl_math_to_gltf_list(obj):
    if isinstance(obj, Quaternion):
        return [obj[1], obj[2], obj[3], obj[0]]
    elif isinstance(obj, Matrix):
        l = []
        row_count = len(obj)
        col_count = len(obj[0])
        for r in range(0, row_count):
            for c in range(0, col_count):
                l.append(obj[r][c])
        return l
    else:
        return list(obj)

def cleanup_keys(d: dict):
    to_pop = []
    for k in d.keys():
        #print(f"{k} is of type {type(d[k])}")
        if d[k] == None or len(d[k]) == 0:
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
            raise Exception(f"Invalid accessor for bone: {accessor}")
        else:
            obj = bpy.data.objects.get((accessor[0], accessor[1]))
            if obj == None:
                raise ObjectNotFoundException(accessor)
            bone = obj.pose.bones[accessor[2]]
            if bone == None:
                raise BoneNotFoundException(accessor)
            return bone

    except Exception as e:
        print(e)
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

def rename_node(bucket, nodeID: int, newName: str):
    node = bucket.data[__k.BUCKET_DATA_NODES][nodeID]
    node[__k.NODE_NAME] = newName

def rename_node(bucket, nodeName: str, newName: str):
    for n in bucket.data[__k.BUCKET_DATA_NODES]:
        if nodeName == n[__k.NODE_NAME]:
            n[__k.NODE_NAME] = newName

def pattern_replace(bucket, dataType: str, pattern: str, newStr: str):
    objects = bucket.data[dataType]
    for obj in objects:
        matches = re.search(pattern, obj["name"])
        for group in matches.groups():
            obj["name"] = obj["name"].replace(group, newStr)

def create_filter(pattern: str, whitelist: bool):
    return (pattern, whitelist)
