from io_advanced_gltf2.Keywords import *
import base64

__GLTF_GLB_PADDING = b"\x00"
__GLTF_EMBEDDED_PADDING = "data:application/octet-stream;base64,"
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

def write_blobs(bucket):
    #TODO: write logic for all file types
    if bucket.settings[BUCKET_SETTING_FILE_TYPE] == FILE_TYPE_GLTF_EMBEDDED:
        for i, buffer in enumerate(bucket.data[BUCKET_DATA_BUFFERS]):
            buffer[BUFFER_BYTE_LENGTH] = len(bucket.blobs[i])
            buffer[BUFFER_URI] += __into_base64(bucket.blobs[i]).decode("utf8")
    else:
        print("file type not yet supported")

def __get_uri(bucket, id):
    setting = bucket.settings[BUCKET_SETTING_FILE_TYPE]

    if setting == FILE_TYPE_GLTF:
        return bucket.settings[BUCKET_SETTING_BINPATH] + str(id) + FILE_EXT_BIN
    if setting == FILE_TYPE_GLB:
        return str(__GLTF_GLB_PADDING, "utf8")
    if setting == FILE_TYPE_GLTF_EMBEDDED:
        return __GLTF_EMBEDDED_PADDING

    
def __into_base64(bytes):
    return base64.b64encode(bytes)