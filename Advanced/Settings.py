from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Keywords import *

def set_setting(bucket: Bucket, setting: str, value):
    bucket.settings[setting] = value

def get_setting(bucket: Bucket, setting: str):
    if not setting in bucket.settings:
        return get_default(setting)
    else:
        return bucket.settings[setting]

def get_default(setting: str):
    default = {
        ####### NODE
        BUCKET_SETTING_REDUNDANCY_CHECK_NODE: False,
        BUCKET_SETTING_NODE_DEFAULT_WORLD_SPACE: True,
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
        ####### SKIN
        BUCKET_SETTING_REDUNDANCY_CHECK_SKIN: True,
        BUCKET_SETTING_INCLUDE_SKIN: True,
        BUCKET_SETTING_SKIN_GET_INVERSED_BINDS: True
    }

    while True:
        yield default[setting]