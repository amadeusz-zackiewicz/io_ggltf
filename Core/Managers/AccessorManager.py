import struct
from io_ggltf.Constants import *
from io_ggltf.Core import Util
from io_ggltf.Core.Managers import BufferViewManager

VECTOR_TYPES = [ACCESSOR_TYPE_VECTOR_2, ACCESSOR_TYPE_VECTOR_3, ACCESSOR_TYPE_VECTOR_4]
MATRIX_TYPES = [ACCESSOR_TYPE_MATRIX_2, ACCESSOR_TYPE_MATRIX_3, ACCESSOR_TYPE_MATRIX_4]
SCALAR_TYPES = [ACCESSOR_TYPE_SCALAR]

def add_accessor(bucket, componentType, type, packingFormat, data: list,
    min = None, max = None, name=None):
    """
    This function does not check for duplicates, it creates an accessor object, buffer view and writes into the buffer, returning the ID

    Args:
        bucket (Bucket): Bucket to write the data into.
        componentType (int): glTF ID for component type, the low component (for example if it's a vector of floats, the this should be ID of float).
        type (str): glTF hint for high component (for example if it's a vector of 3 floats, it would be "VEC3").
        packingFormat (str): packing format to use for the lowest component (using struct module).
        data (list): list of high level data.
        min (int or float): lowest value a component can be
        max (int or float): highest value a component can be
        name (str): optionally name the accessor

    Returns: (int) ID of the new buffer view
    """
    bytes = None
    # create the dictionary for the accessor
    accessor = {
        ACCESSOR_COMPONENT_TYPE: componentType,
        ACCESSOR_TYPE: type,
        ACCESSOR_COUNT: len(data)
    }

    if name != None:
        accessor[ACCESSOR_NAME] = name

    if min != None:
        accessor[ACCESSOR_MIN] = min
    if max != None:
        accessor[ACCESSOR_MAX] = max

    # determine which flattening method to use
    if type in VECTOR_TYPES:
        bytes = __vector_into_bytearray(packingFormat, data)
    elif type in MATRIX_TYPES:
        bytes = __matrix_into_bytearray(packingFormat, data)
    elif type in SCALAR_TYPES:
        bytes = __scalar_into_bytearray(packingFormat, data)
    else:
        bytes = bytearray()

    # assign ID to the accesosr
    accessorID = len(bucket.data[BUCKET_DATA_ACCESSORS])
    # assign ID of the buffer that this accessor describes
    accessor[ACCESSOR_BUFFER_VIEW] = BufferViewManager.add_bytes(bucket, bytes)

    bucket.data[BUCKET_DATA_ACCESSORS].append(accessor)

    return accessorID

def __vector_into_bytearray(format, data: list):
    scalar = []

    for v in data:
        for f in v:
            scalar.append(f)

    return __scalar_into_bytearray(format, scalar)


def __matrix_into_bytearray(format, data: list):

    rowSize = len(data[0].row[0])
    colSize = len(data[0].col[0])

    scalar = []

    for m in data:
        for r in range(rowSize):
            for c in range(colSize):
                scalar.append(m[r][c])

    return __scalar_into_bytearray(format, scalar)

def __scalar_into_bytearray(_format, data: list):
    size = struct.calcsize(_format)
    _bytes = bytearray(size * len(data))
    st = struct.Struct(_format)
    
    for i, s in enumerate(data):
        st.pack_into(_bytes, i * size, s)

    return _bytes