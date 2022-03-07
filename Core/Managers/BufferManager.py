from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Writer
import base64

__GLTF_GLB_PADDING = b"\x00"
__GLTF_EMBEDDED_PREFIX = "data:application/octet-stream;base64,"
__GLTF_EMBEDDED_PADDING_LENGTH = len(__GLTF_EMBEDDED_PREFIX)
__GLTF_GLB_PADDING_LENGTH = len(__GLTF_GLB_PADDING)

def add_bytes(bucket, bytes: bytearray):
    """
    Adds bytes into a fre buffer and returns a tuple:
    (bufferID, byteOffset, byteLength)
    It can be used to contruct a buffer view easily
    """

    bufferID = None
    byteOffset = None
    byteLength = None

    if len(bucket.data[BUCKET_DATA_BUFFERS]) == 0:
        bucket.data[BUCKET_DATA_BUFFERS].append({
            BUFFER_BYTE_LENGTH: 0,
            BUFFER_URI: __get_uri(bucket, 0)
        })
        bucket.blobs.append(bytearray())

    # TODO: buffers have a limit on how much they can contain
    # the manager needs to loop through existing blobs and
    # check if it has enough space to store the new data
    # if not, create a new one
    #
    # for now everything is merged into a massive blob
    # ignoring the issue
    
    #buffer_obj = bucket.data[BUCKET_DATA_BUFFERS][0]

    #if bucket.settings[BUCKET_SETTING_FILE_TYPE] == FILE_TYPE_GLTF_EMBEDDED:
        #bytes = __into_base64(bytes)

    byteLength = len(bytes)
    bufferID = 0
    byteOffset = len(bucket.blobs[0])

    bucket.blobs[0] += bytes
    padding = (4 - (byteLength % 4)) % 4
    bytes += __GLTF_GLB_PADDING * padding


    return (bufferID, byteOffset, byteLength)

def resolve_binaries(bucket):
    """
    For GLTF Embedded:
        Merge blobs into the URI
    For GLTF:
        Dump blobs into binary files in the specified paths.
    For GLB:
        Do nothing, this needs to be handled somewhere else
    """
    #TODO: write logic for all file types
    if bucket.settings[BUCKET_SETTING_FILE_TYPE] == FILE_TYPE_GLTF_EMBEDDED:
        for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
            buffer[BUFFER_BYTE_LENGTH] = len(bucket.blobs[i])
            buffer[BUFFER_URI] += __into_base64(bucket.blobs[i]).decode("utf8")
    elif bucket.settings[BUCKET_SETTING_FILE_TYPE] == FILE_TYPE_GLTF:
        for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
            buffer[BUFFER_BYTE_LENGTH] = len(bucket.blobs[i])
            filepath = bucket.settings[BUCKET_SETTING_FILEPATH] + bucket.settings[BUCKET_SETTING_BINPATH] + str(i)
            Writer.dump_raw_binary(filepath, bucket.blobs[i])
    else:
        return
        

def __get_uri(bucket, id):
    setting = bucket.settings[BUCKET_SETTING_FILE_TYPE]

    if setting == FILE_TYPE_GLTF:
        return bucket.settings[BUCKET_SETTING_BINPATH] + str(id) + FILE_EXT_BIN
    if setting == FILE_TYPE_GLB:
        return str(__GLTF_GLB_PADDING, "utf8")
    if setting == FILE_TYPE_GLTF_EMBEDDED:
        return __GLTF_EMBEDDED_PREFIX

    
def __into_base64(bytes):
    return base64.b64encode(bytes)