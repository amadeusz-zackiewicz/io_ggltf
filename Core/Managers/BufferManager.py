from io_advanced_gltf2.Keywords import *
import base64

__GLTF_GLB_PADDING = b"00"
__GLTF_EMBEDDED_PADDING = "data:application/gltf-buffer;base64,"
__GLTF_EMBEDDED_PADDING_LENGTH = len(__GLTF_EMBEDDED_PADDING)
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
            BUFFER_URI: __get_uri(bucket, 0),
            BUFFER_BYTE_LENGTH: 0
        })

        bucket.blobs.append(bytearray())

    # TODO: buffers have a limit on how much they can contain
    # the manager needs to loop through existing blobs and
    # check if it has enough space to store the new data
    # if not, create a new one
    #
    # for now everything is merged into a massive blob
    # ignoring the issue
    
    buffer_obj = bucket.data[BUCKET_DATA_BUFFERS][0]

    if bucket.settings[BUCKET_SETTING_FILE_TYPE] == FILE_TYPE_GLTF_EMBEDDED:
        bytes = __into_base64(bytes)

    bufferID = 0
    byteOffset = len(bucket.blobs[0])
    byteLength = len(bytes)
    bucket.blobs[0] += bytes

    buffer_obj[BUFFER_BYTE_LENGTH] = len(bucket.blobs[0])

    return (bufferID, byteOffset, byteLength)

def write_blobs(bucket):
    #TODO: write logic for all file types
    for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
        buffer[BUFFER_URI] += str(__into_base64(bucket.blobs[i]), "utf-8")

def __get_uri(bucket, id):
    setting = bucket.settings[BUCKET_SETTING_FILE_TYPE]

    if setting == FILE_TYPE_GLTF:
        return bucket.settings[BUCKET_SETTING_BINPATH] + str(id) + FILE_EXT_BIN
    if setting == FILE_TYPE_GLB:
        return str(__GLTF_GLB_PADDING, "utf-8")
    if setting == FILE_TYPE_GLTF_EMBEDDED:
        return __GLTF_EMBEDDED_PADDING

    
def __into_base64(bytes):
    return base64.standard_b64encode(bytes)