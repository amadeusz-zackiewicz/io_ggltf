from io_ggltf.Constants import *
from io_ggltf.Core.Managers import BufferManager

def add_bytes(bucket, bytes: bytearray, name=None):
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

    if name != None:
        bufferView[BUFFER_VIEW_NAME] = name

    bucket.data[BUCKET_DATA_BUFFER_VIEWS].append(bufferView)


    return bViewID
