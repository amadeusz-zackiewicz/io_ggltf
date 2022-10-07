from io_ggltf.Core.Bucket import Bucket
from io_ggltf import Constants as __c

def set_setting(bucket: Bucket, setting: str, value):
    bucket.settings[setting] = value

def get_setting(bucket: Bucket, setting: str):
    if not setting in bucket.settings:
        return get_default(setting)
    else:
        return bucket.settings[setting]

__default = {
        ####### NODE
        __c.BUCKET_SETTING_REDUNDANCY_CHECK_NODE: False,
        __c.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE: False,
        __c.BUCKET_SETTING_NODE_AUTO_ATTACH_DATA: False,
        ####### MESH
        __c.BUCKET_SETTING_REDUNDANCY_CHECK_MESH: True,
        __c.BUCKET_SETTING_INCLUDE_MESH: True,
        __c.BUCKET_SETTING_MESH_GET_NORMALS: True,
        __c.BUCKET_SETTING_MESH_GET_TANGENTS: False,
        __c.BUCKET_SETTING_MESH_GET_UVS: True,
        __c.BUCKET_SETTING_MESH_GET_VERTEX_COLORS: False,
        __c.BUCKET_SETTING_MESH_GET_BONE_INFLUENCE: True,
        __c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS: False,
        __c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_NORMALS: False,
        __c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_TANGENTS: False,
        __c.BUCKET_SETTING_MESH_GET_SHAPE_KEYS_UV: False,
        __c.BUCKET_SETTING_MESH_MAX_BONES: 4,
        __c.BUCKET_SETTING_MESH_AUTO_ATTACH: True,
        ####### SKIN
        __c.BUCKET_SETTING_REDUNDANCY_CHECK_SKIN: True,
        __c.BUCKET_SETTING_INCLUDE_SKIN: True,
        __c.BUCKET_SETTING_SKIN_GET_INVERSED_BINDS: True,
        __c.BUCKET_SETTING_SKIN_FORCE_REST_POSE: True,
        __c.BUCKET_SETTING_SKIN_RIGIFY_FLAGS: __c.RIGIFY_ONLY_DEFORMS,
        __c.BUCKET_SETTING_SKIN_AUTO_ATTACH: True
    }

def get_default(setting: str):
    return __default[setting]

def get_default():
    return __default