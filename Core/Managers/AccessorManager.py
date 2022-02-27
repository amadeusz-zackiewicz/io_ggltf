import struct
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Core.Managers import BufferViewManager

VECTOR_TYPES = [ACCESSOR_TYPE_VECTOR_2, ACCESSOR_TYPE_VECTOR_3, ACCESSOR_TYPE_VECTOR_4]
MATRIX_TYPES = [ACCESSOR_TYPE_MATRIX_2, ACCESSOR_TYPE_MATRIX_3, ACCESSOR_TYPE_MATRIX_4]
SCALAR_TYPES = [ACCESSOR_TYPE_SCALAR]

def add_accessor(bucket, componentType, type, packingFormat, data: list,
    min = None, max = None):
    """
    This function does not read or add any tracking data,
    it creates an accessor object, buffer view and writes into the buffer
    then adds it into the data and then returns you the ID
    """
    bytes = None

    accessor = {
        ACCESSOR_COMPONENT_TYPE: componentType,
        ACCESSOR_TYPE: type,
        ACCESSOR_COUNT: len(data)
    }

    if min != None:
        accessor[ACCESSOR_MIN] = min
    if max != None:
        accessor[ACCESSOR_MAX] = max

    if type in VECTOR_TYPES:
        bytes = __vector_into_bytearray(packingFormat, data)
    elif type in MATRIX_TYPES:
        bytes = __matrix_into_bytearray(packingFormat, data)
    elif type in SCALAR_TYPES:
        bytes = __scalar_into_bytearray(packingFormat, data)
    else:
        bytes = bytearray()

    accessorID = len(bucket.data[BUCKET_DATA_ACCESSORS])
    accessor[ACCESSOR_BUFFER_VIEW] = BufferViewManager.add_bytes(bucket, bytes)

    bucket.data[BUCKET_DATA_ACCESSORS].append(accessor)

    return accessorID

    


def __pack_vector_elements(bytes, obj, format):
    for f in obj:
        bytes += struct.pack(format, f)

def __vector_into_bytearray(format, data: list):
    scalar = []

    for v in data:
        for f in v:
            scalar.append(f)

    return __scalar_into_bytearray(format, scalar)


def __matrix_into_bytearray(data: list):
    pass

def __scalar_into_bytearray(format, data: list):
    size = struct.calcsize(format)
    bytes = bytearray(size * len(data))

    for i, s in enumerate(data):
        struct.pack_into(format, bytes, i * size, s)

    return bytes