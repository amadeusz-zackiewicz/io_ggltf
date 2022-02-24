from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Managers import BufferManager

def add_bytes(bucket, bytes: bytearray):
    """
    Returns ID of the new buffer view that is used to access the given bytes
    """

    bufferID, byteOffset, byteLength = BufferManager.add_bytes(bucket, bytes)

    bViewID = len(bucket.data[BUCKET_DATA_BUFFER_VIEWS])

    bufferView = {
        BUFFER_VIEW_BUFFER: bufferID,
        BUFFER_VIEW_BYTE_OFFSET: byteOffset,
        BUFFER_VIEW_BYTE_LENGTH: byteLength
    }

    bucket.data[BUCKET_DATA_BUFFER_VIEWS].append(bufferView)

    return bViewID
