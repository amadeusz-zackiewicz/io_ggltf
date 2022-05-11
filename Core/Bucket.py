from io_advanced_gltf2.Keywords import *
import bpy

class Bucket():
    def __init__(self, 
    filePath,
    fileName, 
    binPath,
    fileType = FILE_TYPE_GLTF_EMBEDDED,
    dependencyGraph = None
    ):
        self.settings = {
            BUCKET_SETTING_FILEPATH : filePath,
            BUCKET_SETTING_FILENAME : fileName,
            BUCKET_SETTING_BINPATH : binPath,
            BUCKET_SETTING_FILE_TYPE: fileType,
            ####### MESH
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
            BUCKET_SETTING_INCLUDE_SKIN: True,
            BUCKET_SETTING_SKIN_GET_INVERSED_BINDS: True
        }
        self.data = {
            BUCKET_DATA_EXTENSIONS_USED : [],
            BUCKET_DATA_EXTENSIONS_REQUIRED : [],
            BUCKET_DATA_ANIMATIONS : [],
            BUCKET_DATA_ASSET : {"generator": "Blender Advanced GLTF2 I/O", "version" : "2.0"},
            BUCKET_DATA_SCENES : [],
            BUCKET_DATA_NODES : [],
            BUCKET_DATA_CAMERAS : [],
            BUCKET_DATA_IMAGES : [],
            BUCKET_DATA_MATERIALS : [{
                MATERIAL_NAME: "default_temp_material",
                MATERIAL_DOUBLE_SIDED: False,
                MATERIAL_ALPHA_MODE: "OPAQUE",
                "pbrMetallicRoughness":{
                    "baseColorFactor":
                    [
                        0.8,
                        0.8,
                        0.8,
                        1.0
                    ],
                    "metallicFactor": 0,
                    "roughnessFactor": 0.4
                }
            }],# TODO: remember to delete the temp material creation when materials are supported
            BUCKET_DATA_MESHES : [],
            BUCKET_DATA_SAMPLERS : [],
            BUCKET_DATA_SKINS : [],
            BUCKET_DATA_TEXTURES : [],
            BUCKET_DATA_EXTENSIONS : [],
            BUCKET_DATA_EXTRAS : [],
            BUCKET_DATA_ACCESSORS : [],
            BUCKET_DATA_BUFFER_VIEWS : [],
            BUCKET_DATA_BUFFERS : []
        }
        self.trackers = {
            BUCKET_TRACKER_NODES : {},
            BUCKET_TRACKER_MESHES : {},
            BUCKET_TRACKER_MESH_ATTRIBUTE : {}
        }
        self.blobs = []
        self.currentDependencyGraph = bpy.context.evaluated_depsgraph_get() if dependencyGraph == None else dependencyGraph
        self.skinDefinition = []