from fileinput import filename
import os
import json
import struct
import bpy
from io_advanced_gltf2.Core.Managers import BufferManager
from io_advanced_gltf2.Core.Util import cleanup_keys
from io_advanced_gltf2.Keywords import *

# https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.pdf ----- 4.4 glTF Layout
__BINARY_MAGIC_NUMBER = 0x46546C67
__BINARY_JSON_NUMBER = 0x4E4F534A
__BINARY_CHUNK_NUMBER = 0x004E4942
__BINARY_JSON_PAD = b" "
__BINARY_PAD = b"\0"
__BINARY_VERSION_NUMBER = 2

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

    f.write(struct.pack(PACKING_FORMAT_U_INT, __BINARY_MAGIC_NUMBER))
    f.write(struct.pack(PACKING_FORMAT_U_INT, __BINARY_VERSION_NUMBER))
    f.write(struct.pack(PACKING_FORMAT_U_INT, 0)) # temporarily write empty bytes where the file size should be
    f.write(struct.pack(PACKING_FORMAT_U_INT, js_len))
    f.write(struct.pack(PACKING_FORMAT_U_INT, __BINARY_JSON_NUMBER))
    f.write(js)
    f.write(__BINARY_JSON_PAD * (len(js) % 4))

    for b in blobs:
        f.write(struct.pack(PACKING_FORMAT_U_INT, len(b) + len(b) % 4))
        f.write(struct.pack(PACKING_FORMAT_U_INT, __BINARY_CHUNK_NUMBER))
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