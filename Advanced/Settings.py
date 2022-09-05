from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Keywords import *

def set_setting(bucket: Bucket, setting: str, value):
    bucket.settings[setting] = value

def get_setting(bucket: Bucket, setting: str):
    if not setting in bucket.settings:
        return get_default(setting)
    else:
        return bucket.settings[setting]

__default = {
        ####### NODE
        BUCKET_SETTING_REDUNDANCY_CHECK_NODE: False,
        BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE: True,
        ####### MESH
        BUCKET_SETTING_REDUNDANCY_CHECK_MESH: True,
        BUCKET_SETTING_INCLUDE_MESH: True,
        BUCKET_SETTING_MESH_GET_NORMALS: True,
        BUCKET_SETTING_MESH_GET_TANGENTS: False,
        BUCKET_SETTING_MESH_GET_UVS: True,
        BUCKET_SETTING_MESH_GET_VERTEX_COLORS: False,
        BUCKET_SETTING_MESH_GET_BONE_INFLUENCE: True,
        BUCKET_SETTING_MESH_GET_SHAPE_KEYS: False,
        BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS: False,
        BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS: False,
        BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV: False,
        BUCKET_SETTING_MESH_MAX_BONES: 4,
        ####### SKIN
        BUCKET_SETTING_REDUNDANCY_CHECK_SKIN: True,
        BUCKET_SETTING_INCLUDE_SKIN: True,
        BUCKET_SETTING_SKIN_GET_INVERSED_BINDS: True,
        BUCKET_SETTING_SKIN_FORCE_REST_POSE: True
    }

def get_default(setting: str):
    return __default[setting]

def get_default():
    return __default