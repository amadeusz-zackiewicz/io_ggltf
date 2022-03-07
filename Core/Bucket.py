from io_advanced_gltf2.Keywords import *

class Bucket():
    def __init__(self, 
    filePath,
    fileName, 
    binPath,
    fileType = FILE_TYPE_GLTF_EMBEDDED,
    y_up = True, 
    mode = COLLECT_MODE_SIMPLE,
    collectTypes = [BLENDER_TYPE_EMPTY]
    ):
        self.settings = {
            BUCKET_SETTING_FILEPATH : filePath,
            BUCKET_SETTING_FILENAME : fileName,
            BUCKET_SETTING_BINPATH : binPath,
            BUCKET_SETTING_Y_UP : y_up,
            BUCKET_SETTING_COLLECT_MODE : mode,
            BUCKET_SETTING_COLLECT_TYPES : collectTypes,
            BUCKET_SETTING_FILE_TYPE: fileType
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
            BUCKET_TRACKER_MESHES : {}
        }
        self.blobs = []