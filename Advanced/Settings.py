from io_ggltf.Core.Bucket import Bucket
from io_ggltf import Constants as __c
from io_ggltf.Core import ShowFunction
from warnings import deprecated

@deprecated("Advanced.Settings.set_setting is deprecated, it will be removed in future versions and might not function as intended.")
def set_setting(bucket: Bucket, setting: str, value):
    bucket.settings[setting] = value

@deprecated("Advanced.Settings.get_setting is deprecated, it will be removed in future versions and might not function as intended.")
def get_setting(bucket: Bucket, setting: str):
    if not setting in bucket.settings:
        return get_default_dict(setting)
    else:
        return bucket.settings[setting]

__default = {
        ####### ANIMATION
        __c.BUCKET_SETTING_FRAME_STEP: 1.0,
        __c.BUCKET_SETTING_STEP_INTERPOLATION: False,
        __c.BUCKET_SETTING_OPTIMISE_ANIMATION: True,
        ####### NODE
        __c.BUCKET_SETTING_REDUNDANCY_CHECK_NODE: False,
        __c.BUCKET_SETTING_NODE_DEFAULT_PARENT_SPACE: False,
        __c.BUCKET_SETTING_NODE_AUTO_ATTACH_DATA: False,
        __c.BUCKET_SETTING_ENFORCE_SCENE: True,
        __c.BUCKET_SETTING_TEXT_PRECISION: 6,
        __c.BUCKET_SETTING_BINARY_PRECISION: 7,
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

@deprecated("Advanced.Settings.get_default is deprecated, it will be removed in future versions and might not function as intended.")
def get_default(setting: str):
    return __default[setting]

@deprecated("Advanced.Settings.get_default_dict is deprecated, it will be removed in future versions and might not function as intended.")
def get_default_dict():
    return __default

#ShowFunction.Register(set_setting, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Settings-Module#set_setting")
#ShowFunction.Register(get_setting, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Settings-Module#get_setting")
#ShowFunction.Register(get_default, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Settings-Module#get_default")