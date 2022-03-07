from fileinput import filename
import os
import json
import struct
from io_advanced_gltf2.Core.Managers import BufferManager
from io_advanced_gltf2.Core.Util import cleanup_keys
from io_advanced_gltf2.Keywords import *

__BINARY_MAGIC_NUMBER = b"glTF"
__BINARY_VERSION_NUMBER = struct.pack(PACKING_FORMAT_U_INT, 2)
__BINARY_PAD = b"00"

def dump_bucket(bucket):
    __to_gltf(bucket)

def __to_gltf(bucket):
    __ensure_scene(bucket)

    ## this will write raw binaries if the file type is gltf
    BufferManager.resolve_binaries(bucket)

    cleanup_keys(bucket.data)
    bucket.data["scene"] = 0 # TODO: add a setting for auto scene creation

    fileType = bucket.settings[BUCKET_SETTING_FILE_TYPE]
    filePath = bucket.settings[BUCKET_SETTING_FILEPATH] + bucket.settings[BUCKET_SETTING_FILENAME]

    if fileType == FILE_TYPE_GLTF or fileType == FILE_TYPE_GLTF_EMBEDDED:
        dump_gltf(filePath, bucket.data)
    else:
        dump_glb(filePath, bucket.data, bucket.blobs)

def __ensure_scene(bucket):
    if len(bucket.data[BUCKET_DATA_SCENES]) > 0:
        return
        
    nodes = bucket.data[BUCKET_DATA_NODES]
    top_obj = []
    node_id = []

    scene = {SCENE_NAME : "scene"}

    for n in nodes:
        top_obj.append(True)

    for n in nodes:
        if NODE_CHILDREN in n:
            for c in n[NODE_CHILDREN]:
                top_obj[c] = False

    for i in range(0, len(top_obj)):
        if top_obj[i]:
            node_id.append(i)

    scene[SCENE_NODES] = node_id

    bucket.data[BUCKET_DATA_SCENES].append(scene)

def __prep_path(path : str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def dump_gltf(path : str, data):
    """
    Path needs to include name, without extension
    """
    __prep_path(path)
    f = open(path + FILE_EXT_GLTF, "w")
    _ = json.dump(data, f, indent=4)
    f.close()

def dump_glb(path : str, data, blobs):
    __prep_path(path)

            
def dump_raw_binary(path : str, bytes : bytearray):
    """
    Path needs to include file name, without extension
    """
    __prep_path(path)
    f = open(path + FILE_EXT_BIN, "wb")
    #length = len(bytes) + len(__BINARY_MAGIC_NUMBER) + len(__BINARY_VERSION_NUMBER) + 4
    f.write(bytes)
    f.close()