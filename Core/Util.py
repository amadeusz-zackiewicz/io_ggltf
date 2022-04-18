from io_advanced_gltf2.Keywords import *
from mathutils import Matrix, Vector, Quaternion, Euler
from bpy_extras.io_utils import axis_conversion

def matrix_ensure_coord_space(org_mat : Matrix) -> Matrix:
    return get_basis_matrix_conversion() @ org_mat

def location_ensure_coord_space(org_loc : Vector) -> Vector:
    return Vector((org_loc[0], org_loc[2], -org_loc[1]))


def rotation_ensure_coord_space(org_rot : Quaternion) -> Quaternion:
    return Quaternion((org_rot[0], org_rot[1], org_rot[3], -org_rot[2]))


def scale_ensure_coord_space(org_scl : Vector) -> Vector:
    return Vector((org_scl[0], org_scl[2], org_scl[1]))


def direction_ensure_coord_space(org_dir: Vector) -> Vector:
    return Vector((org_dir[0], org_dir[2], -org_dir[1]))

def uv_ensure_coord_space(org_uv: Vector) -> Vector:
    org_uv[1] = 1 - org_uv[1]
    return org_uv

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

def validate_filter_list(obj, filter, expected_type = str) -> list:
    if type(obj) != list:
        if obj == None: 
            if filter == LIST_FILTER_WHITELIST:
                return None
            else:
                obj = []
        else:
            obj = [obj]

    for o in enumerate(obj):
        if type(o[1]) != expected_type:
            print(str(o[1]) + f" is a wrong variable type, expected: {expected_type}, got: {type(o[1])}")
            obj.pop(o[0])

    if len(obj) == 0 and filter == LIST_FILTER_WHITELIST:
        return None

    return obj

def get_basis_matrix_conversion():
    convert = axis_conversion(from_forward="-Y", from_up="Z", to_forward="Z", to_up="Y")
    convert.resize_4x4()
    return convert