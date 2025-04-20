import Constants as C
from . import CompareCommon
import struct
import os

def is_buffer_internal(bufferDict) -> bool:
	if not C.BUFFER_URI in bufferDict or bufferDict[C.BUFFER_URI].find(C.FILE_INTERNAL_BASE64_PREFIX, 0, len(C.FILE_INTERNAL_BASE64_PREFIX) + 4) > -1:
		return True
	else:
		return False
	
def get_external_buffer_path(mainFilePath, bufferDict):
	return os.path.join(os.path.dirname(mainFilePath), bufferDict[C.BUFFER_URI])


def compare_buffer(originalBuffer, testBuffer, originalByteOffset, testByteOffset, byteLenght, floatTolerance, componentType, groupingType, ownerHint) -> str:
	errStr = ""

	if originalBuffer == None:
		errStr += f"Buffer in original file belonging to {ownerHint} is missing.\n"
	if testBuffer == None:
		errStr += f"Buffer in test file belonging to {ownerHint} is missing.\n"

	if errStr != "":
		return errStr
	
	originalArray = _unpack_components(originalBuffer, originalByteOffset, byteLenght, componentType)
	testArray = _unpack_components(testBuffer, testByteOffset, byteLenght, componentType)

	if CompareCommon.is_component_type_floaty(componentType):
		errStr += _compare_floats(originalArray, testArray, groupingType, floatTolerance, ownerHint)
	else:
		errStr += _compare_other(originalArray, testArray, groupingType, ownerHint)

	return errStr

def _unpack_components(buffer, byteOffset, byteLength, componentType) -> list:
	packingFormat = C.PACKING_FORMAT_U_CHAR

	if componentType == C.ACCESSOR_COMPONENT_TYPE_FLOAT:
		packingFormat = C.PACKING_FORMAT_FLOAT
	elif componentType == C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_INT:
		packingFormat = C.PACKING_FORMAT_U_INT
	elif componentType == C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT:
		packingFormat == C.PACKING_FORMAT_U_SHORT
	elif componentType == C.ACCESSOR_COMPONENT_TYPE_SHORT:
		packingFormat = C.PACKING_FORMAT_SHORT

	unpackedList = []

	for value in struct.iter_unpack(packingFormat, buffer[byteOffset:byteLength]):
		unpackedList.append(value[0])

	return unpackedList

def _get_grouping_type_size(groupingType) -> int:
	match groupingType:
		case C.ACCESSOR_TYPE_SCALAR:
			return 1
		case C.ACCESSOR_TYPE_VECTOR_2:
			return 2
		case C.ACCESSOR_TYPE_VECTOR_3:
			return 3
		case C.ACCESSOR_TYPE_VECTOR_4:
			return 4
		case C.ACCESSOR_TYPE_MATRIX_2:
			return 4
		case C.ACCESSOR_TYPE_MATRIX_3:
			return 9
		case C.ACCESSOR_TYPE_MATRIX_4:
			return 16
	
	return 0

def _compare_floats(originalArray, testArray, groupingType, floatTolerance, ownerHint) -> str:
	errStr = ""

	storageTypeSize = _get_grouping_type_size(groupingType)

	if len(originalArray) % storageTypeSize > 0:
		errStr += f"Original buffer belonging to {ownerHint} has incorrect size (stray count: {len(originalArray) % storageTypeSize}) of components for {groupingType}, expected multiples of {storageTypeSize}.\n"
	if len(testArray) % storageTypeSize > 0:
		errStr += f"Test buffer belonging to {ownerHint} has incorrect size (stray count: {len(testArray) % storageTypeSize}) of components for {groupingType}, expected multiples of {storageTypeSize}.\n"

	if errStr != "":
		return errStr
	
	i = 0
	while i <= len(originalArray):

		originalSlice = originalArray[i:i + storageTypeSize]
		testSlice = testArray[i:i + storageTypeSize]
		bufferCompareStr = ""

		bufferCompareStr += CompareCommon.compare_float_array(storageTypeSize, originalSlice, testSlice, ownerHint, groupingType, C.GLTF_BUFFER, floatTolerance)
		if bufferCompareStr != "":
			errStr += f"Buffer mismatch between {ownerHint}:\n\t{originalArray}\n\t{testArray}\n"
			break

		i += storageTypeSize

	#errStr += f"Info: {ownerHint}:\n\t{originalArray}\n\t{testArray}\n"

	return errStr

def _compare_other(originalArray, testArray, groupingType, ownerHint) -> str:
	errStr = ""

	storageTypeSize = _get_grouping_type_size(groupingType)

	if len(originalArray) % storageTypeSize > 0:
		errStr += f"Original buffer belonging to {ownerHint} has incorrect size (stray count: {len(originalArray) % storageTypeSize}) of components for {groupingType}, expected multiples of {storageTypeSize}.\n"
	if len(testArray) % storageTypeSize > 0:
		errStr += f"Test buffer belonging to {ownerHint} has incorrect size (stray count: {len(testArray) % storageTypeSize}) of components for {groupingType}, expected multiples of {storageTypeSize}.\n"

	if errStr != "":
		return errStr
	
	i = 0
	while i <= len(originalArray):

		originalSlice = originalArray[i:i + storageTypeSize]
		testSlice = testArray[i:i + storageTypeSize]
		bufferCompareStr = ""

		bufferCompareStr += CompareCommon.compare_array(len(originalSlice), originalSlice, testSlice, ownerHint, groupingType, C.GLTF_BUFFER)
		if bufferCompareStr != "":
			errStr += f"Buffer mismatch between {ownerHint}:\n\t{originalArray}\n\t{testArray}\n"
			break

		i += storageTypeSize

	#errStr += f"Info: {ownerHint}:\n\t{originalArray}\n\t{testArray}\n"

	return errStr