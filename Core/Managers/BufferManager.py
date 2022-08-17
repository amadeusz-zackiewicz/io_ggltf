from io_ggltf.Keywords import *
from io_ggltf.Core import Writer
import os
import base64

__GLTF_GLB_PADDING = b"\x00"
__GLTF_EMBEDDED_PREFIX = "data:application/octet-stream;base64,"

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
        buffer = {}
        buffer[BUFFER_BYTE_LENGTH] = 0

        if bucket.settings[BUCKET_SETTING_FILE_TYPE] != FILE_TYPE_GLB:
            buffer[BUFFER_URI] = __get_uri(bucket, 0)

        bucket.data[BUCKET_DATA_BUFFERS].append(buffer)
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

    fileType = bucket.settings[BUCKET_SETTING_FILE_TYPE]

    if fileType == FILE_TYPE_GLTF_EMBEDDED:
        for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
            buffer[BUFFER_BYTE_LENGTH] = len(bucket.blobs[i])
            buffer[BUFFER_URI] += __into_base64(bucket.blobs[i]).decode("utf8")
    elif fileType == FILE_TYPE_GLTF:
        for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
            buffer[BUFFER_BYTE_LENGTH] = len(bucket.blobs[i])
            filepath = os.path.abspath(bucket.settings[BUCKET_SETTING_FILEPATH] + bucket.data[BUCKET_DATA_BUFFERS][i][BUFFER_URI]) # the URI should be the relative path from the main file, we convert it to the real absolute path
            Writer.dump_raw_binary(filepath, bucket.blobs[i])
    elif fileType == FILE_TYPE_GLB:
        for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
            buffer[BUFFER_BYTE_LENGTH] = len(bucket.blobs[i])

        

def __get_uri(bucket, id):
    fileType = bucket.settings[BUCKET_SETTING_FILE_TYPE]

    if fileType == FILE_TYPE_GLTF:
        return bucket.settings[BUCKET_SETTING_BINPATH] + bucket.settings[BUCKET_SETTING_FILENAME]+ "_" + str(id) + FILE_EXT_BIN
    if fileType == FILE_TYPE_GLTF_EMBEDDED:
        return __GLTF_EMBEDDED_PREFIX

    
def __into_base64(bytes):
    return base64.b64encode(bytes)