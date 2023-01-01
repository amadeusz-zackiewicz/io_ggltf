import struct
from io_ggltf import Constants as __c
from io_ggltf.Core import Util
from io_ggltf.Core.Managers import BufferViewManager
import mathutils

VECTOR_TYPES = [__c.ACCESSOR_TYPE_VECTOR_2, __c.ACCESSOR_TYPE_VECTOR_3, __c.ACCESSOR_TYPE_VECTOR_4]
MATRIX_TYPES = [__c.ACCESSOR_TYPE_MATRIX_2, __c.ACCESSOR_TYPE_MATRIX_3, __c.ACCESSOR_TYPE_MATRIX_4]
SCALAR_TYPES = [__c.ACCESSOR_TYPE_SCALAR]

def add_accessor(bucket, componentType, type, packingFormat, data: list,
    min = None, max = None, name=None, overridePrecision=None):
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
        overridePrecision (bool): Override decimal point for rounding floating point numbers

    Returns: (int) ID of the new buffer view
    """
    if componentType == None:
        componentType = assume_component_type(data)
    if type == None:
        type = assume_type(data)
    if packingFormat == None:
        packingFormat = assume_packing_format(data)

    bytes = None
    # create the dictionary for the accessor
    accessor = {
        __c.ACCESSOR_COMPONENT_TYPE: componentType,
        __c.ACCESSOR_TYPE: type,
        __c.ACCESSOR_COUNT: len(data)
    }

    if name != None:
        accessor[__c.ACCESSOR_NAME] = name

    if min != None:
        accessor[__c.ACCESSOR_MIN] = min
    if max != None:
        accessor[__c.ACCESSOR_MAX] = max

    if overridePrecision: floatPrecision = overridePrecision
    else: floatPrecision = bucket.settings[__c.BUCKET_SETTING_BINARY_PRECISION]

    # determine which flattening method to use
    if type in VECTOR_TYPES:
        bytes = __vector_into_bytearray(packingFormat, data, floatPrecision)
    elif type in MATRIX_TYPES:
        bytes = __matrix_into_bytearray(packingFormat, data, floatPrecision)
    elif type in SCALAR_TYPES:
        bytes = __scalar_into_bytearray(packingFormat, data, floatPrecision)
    else:
        bytes = bytearray()

    # assign ID to the accesosr
    accessorID = len(bucket.data[__c.BUCKET_DATA_ACCESSORS])
    # assign ID of the buffer that this accessor describes
    accessor[__c.ACCESSOR_BUFFER_VIEW] = BufferViewManager.add_bytes(bucket, bytes)

    bucket.data[__c.BUCKET_DATA_ACCESSORS].append(accessor)

    return accessorID

def __vector_into_bytearray(format, data: list, floatPrecision: int):
    scalar = []

    if type(data[0]) == mathutils.Quaternion:
        for q in data:
            scalar.extend(Util.bl_math_to_gltf_list(q))
    else:
        for v in data:
            for f in v:
                scalar.append(f)

    return __scalar_into_bytearray(format, scalar, floatPrecision)


def __matrix_into_bytearray(format, data: list, floatPrecision: int):

    rowSize = len(data[0].row[0])
    colSize = len(data[0].col[0])

    scalar = []

    for m in data:
        for r in range(rowSize):
            for c in range(colSize):
                scalar.append(m[r][c])

    return __scalar_into_bytearray(format, scalar, floatPrecision)

def __scalar_into_bytearray(_format, data: list, floatPrecision: int):
    size = struct.calcsize(_format)
    _bytes = bytearray(size * len(data))
    st = struct.Struct(_format)

    if type(data[0]) == float and floatPrecision >= 0:
        Util.round_float_list_to_precision(data, floatPrecision) 

    for i, s in enumerate(data):
        st.pack_into(_bytes, i * size, s)

    return _bytes

__vector_types = [None, None, __c.ACCESSOR_TYPE_VECTOR_2, __c.ACCESSOR_TYPE_VECTOR_3, __c.ACCESSOR_TYPE_VECTOR_4]
__matrix_types = [None, None, __c.ACCESSOR_TYPE_MATRIX_2, __c.ACCESSOR_TYPE_MATRIX_3, __c.ACCESSOR_TYPE_MATRIX_4]

def assume_type(data: list):
    typeOf = type(data[0])
    if typeOf == int or typeOf == float or typeOf == bool:
        return __c.ACCESSOR_TYPE_SCALAR
    if typeOf == mathutils.Vector:
        length = len(data[0])
        try: return __vector_types[length]
        except: return None
    if typeOf == mathutils.Quaternion:
        return __c.ACCESSOR_TYPE_VECTOR_4
    if typeOf == mathutils.Matrix:
        row = len(data[0])
        col = len(data[0][0])
        if row != col: return None
        return __matrix_types[row]

def assume_component_type(data: list):
    typeOf = type(data[0])
    if typeOf == mathutils.Vector:
        if type(data[0][0]) == float:
            return __c.ACCESSOR_COMPONENT_TYPE_FLOAT
        if type(data[0][0]) == int:
            return __c.ACCESSOR_COMPONENT_TYPE_SHORT
    if typeOf == float or typeOf == mathutils.Quaternion or typeOf == mathutils.Matrix:
        return __c.ACCESSOR_COMPONENT_TYPE_FLOAT
    if typeOf == int:
        return __c.ACCESSOR_COMPONENT_TYPE_SHORT
    if typeOf == bool:
        return __c.ACCESSOR_COMPONENT_TYPE_BYTE
    

def assume_packing_format(data: list):
    typeOf = type(data[0])
    if typeOf == mathutils.Vector:
        if type(data[0][0]) == float:
            return __c.PACKING_FORMAT_FLOAT
        if type(data[0][0]) == int:
            return __c.PACKING_FORMAT_SHORT
    if typeOf == float or typeOf == mathutils.Quaternion or typeOf == mathutils.Matrix:
        return __c.PACKING_FORMAT_FLOAT
    if typeOf == int:
        return __c.PACKING_FORMAT_SHORT
    if typeOf == bool:
        return __c.PACKING_FORMAT_BOOL
