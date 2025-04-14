import os
import json
import struct
import bpy
from io_ggltf.Core.Managers import BufferManager
from io_ggltf.Core.Util import cleanup_keys
from io_ggltf.Constants import *
from io_ggltf.Core import Collector

# https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf ----- 4.4 glTF Layout
__BINARY_JSON_PAD = b" "
__BINARY_PAD = b"\0"
__BINARY_VERSION_NUMBER = 2

def stage_bucket(bucket):
    Collector.collect(bucket)
    if bucket.settings[BUCKET_SETTING_ENFORCE_SCENE]:
        __ensure_scene(bucket)

def dump_bucket(bucket):
    stage_bucket(bucket)

    ## this will write raw binaries if the file type is gltf
    BufferManager.resolve_binaries(bucket)

    cleanup_keys(bucket.data)

    fileType = bucket.settings[BUCKET_SETTING_FILE_TYPE]
    filePath = bucket.settings[BUCKET_SETTING_FILEPATH] + bucket.settings[BUCKET_SETTING_FILENAME]

    if fileType == FILE_TYPE_GLTF or fileType == FILE_TYPE_GLTF_EMBEDDED:
        dump_gltf(filePath, bucket.data)
    else:
        dump_glb(filePath, bucket.data, bucket.blobs)

    del bucket

def __ensure_scene(bucket):
    if len(bucket.data[BUCKET_DATA_SCENES]) > 0:
        if "scene" not in bucket.data:
            bucket.data["scene"] = 0
        return
        
    nodes = bucket.data[BUCKET_DATA_NODES]
    isTopObject = []
    nodeIDs = []

    for n in nodes:
        isTopObject.append(True)

    for n in nodes:
        if NODE_CHILDREN in n:
            for c in n[NODE_CHILDREN]:
                isTopObject[c] = False

    for i in range(0, len(isTopObject)):
        if isTopObject[i]:
            nodeIDs.append(i)

    if len(nodeIDs) > 0:
        scene = {
            SCENE_NAME : "scene",
            SCENE_NODES : nodeIDs
        }

        bucket.data[BUCKET_DATA_SCENES].append(scene)
        bucket.data["scene"] = 0

def __prep_path(path : str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def dump_gltf(path : str, data):
    """
    Path needs to include file name, without extension
    """
    __prep_path(path)
    f = open(path + FILE_EXT_GLTF, "w")
    json.dump(data, f, indent=4)
    f.close()

def dump_glb(path : str, data, blobs):
    """
    Path needs to include file name, without extension
    """
    js = bytes(json.dumps(data).encode("ascii"))
    js_len = len(js) + len(js) % 4

    __prep_path(path)
    f = open(path + FILE_EXT_GLB, "w+b")

    f.write(struct.pack(PACKING_FORMAT_U_INT, FILE_BIN_MAGIC_NUMBER))
    f.write(struct.pack(PACKING_FORMAT_U_INT, __BINARY_VERSION_NUMBER))
    f.write(struct.pack(PACKING_FORMAT_U_INT, 0)) # temporarily write empty bytes where the file size should be
    f.write(struct.pack(PACKING_FORMAT_U_INT, js_len))
    f.write(struct.pack(PACKING_FORMAT_U_INT, FILE_BIN_CHUNK_TYPE_JSON))
    f.write(js)
    f.write(__BINARY_JSON_PAD * (len(js) % 4))

    for b in blobs:
        f.write(struct.pack(PACKING_FORMAT_U_INT, len(b) + len(b) % 4))
        f.write(struct.pack(PACKING_FORMAT_U_INT, FILE_BIN_CHUNK_TYPE_BIN))
        f.write(b)
        f.write(__BINARY_PAD * (len(b) % 4))
    
    # use current cursor position to determine the file size
    fileLength = f.tell()

    f.seek(8) # seek to where the file length is supposed to be
    f.write(struct.pack(PACKING_FORMAT_U_INT, fileLength)) # overwrite the temporary size of 0 to real size

    f.close()

            
def dump_raw_binary(path : str, bytes : bytearray):
    """
    Path needs to include file name, without extension
    """
    __prep_path(path)
    f = open(path, "wb")
    f.write(bytes)
    f.write(__BINARY_PAD * (len(bytes) % 4))
    f.close()