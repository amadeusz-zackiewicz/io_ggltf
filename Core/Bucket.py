from io_ggltf.Keywords import *
import bpy
import os

class Bucket():
    def __init__(self, 
    filePath,
    fileName, 
    binPath,
    fileType = FILE_TYPE_GLTF_EMBEDDED,
    dependencyGraph = None
    ):

        filePath = os.path.abspath(bpy.path.abspath(filePath))
        if filePath[-1] != os.path.sep:
            filePath = filePath + os.path.sep

        self.__get_default_settings(filePath, fileName, binPath, fileType)
        self.__fill_in_data()
        self.blobs = []
        self.currentDependencyGraph = bpy.context.evaluated_depsgraph_get() if dependencyGraph == None else dependencyGraph
        self.skinDefinition = []
        self.commandQueue = []
        for _ in range(BUCKET_COMMAND_QUEUE_TYPES):
            self.commandQueue.append([])
        self.redundancies = {}
        self.preScoopCounts = { # used to determine which ID the specific data will occupy before commiting
            BUCKET_DATA_SCENES: 0,
            BUCKET_DATA_NODES: 0,
            BUCKET_DATA_MESHES: 0,
            BUCKET_DATA_SKINS: 0
        }
        self.accessors = { # to get accessor from the assigned ID
            BUCKET_DATA_NODES: {},
            BUCKET_DATA_MESHES: {},
            BUCKET_DATA_SKINS: {}
        }

    def __fill_in_data(self) -> dict:
        self.data = {
            BUCKET_DATA_EXTENSIONS_USED : [],
            BUCKET_DATA_EXTENSIONS_REQUIRED : [],
            BUCKET_DATA_ANIMATIONS : [],
            BUCKET_DATA_ASSET : {"generator": "Blender ggltf", "version" : "2.0"},
            BUCKET_DATA_SCENES : [],
            BUCKET_DATA_NODES : [],
            BUCKET_DATA_CAMERAS : [],
            BUCKET_DATA_IMAGES : [],
            BUCKET_DATA_MATERIALS : [],
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

    def __get_default_settings(self, filePath, fileName, binPath, fileType) -> dict:
        self.settings = {
            BUCKET_SETTING_FILEPATH : filePath,
            BUCKET_SETTING_FILENAME : fileName,
            BUCKET_SETTING_BINPATH : binPath,
            BUCKET_SETTING_FILE_TYPE: fileType,
        }

