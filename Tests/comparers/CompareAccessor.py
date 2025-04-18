import Constants as C
from . import CompareCommon

def compare_accessor(originalAccessor, testAccessor, originalBuffersCache, testBuffersCache, floatTolerance, originalGltf, testGltf, idHint) -> str:
	errStr = ""

	errStr += CompareCommon.compare_name(originalAccessor, testAccessor, C.GLTF_ACCESSOR, idHint)
	accessorName = originalAccessor.get(C.ACCESSOR_NAME, idHint)

	# required first
	errStr += _compare_component_type(originalAccessor, testAccessor, accessorName)
	errStr += _compare_count(originalAccessor, testAccessor, accessorName)
	errStr += _compare_type(originalAccessor, testAccessor, accessorName)

	if errStr != "": # if requird keys have issues then skip the rest
		return errStr
	
	componentType = originalAccessor[C.ACCESSOR_COMPONENT_TYPE]

	# non required
	# byte offset is already contained within buffer view, so its pointless double it up here
	if componentType == C.ACCESSOR_COMPONENT_TYPE_FLOAT or componentType == C.ACCESSOR_COMPONENT_TYPE_SHORT or componentType == C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT:
		errStr += _compare_max_float(originalAccessor, testAccessor, accessorName, floatTolerance)
		errStr += _compare_min_float(originalAccessor, testAccessor, accessorName, floatTolerance)
	else:
		errStr += _compare_max_other(originalAccessor, testAccessor, accessorName)
		errStr += _compare_min_other(originalAccessor, testAccessor, accessorName)

	return errStr

def _compare_component_type(originalAccessor, testAccessor, idHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.ACCESSOR_COMPONENT_TYPE, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	originalType = originalAccessor[C.ACCESSOR_COMPONENT_TYPE]
	testType = testAccessor[C.ACCESSOR_COMPONENT_TYPE]

	if originalType != testType:
		errStr += f"Accessor <{idHint}> mismatch of required key: {C.ACCESSOR_COMPONENT_TYPE}\n\t{originalType}\n\t{testType}"

	return errStr

def _compare_count(originalAccessor, testAccessor, idHint) -> str:
	errStr += ""

	errStr += CompareCommon.check_required_key(C.ACCESSOR_COUNT, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	originalCount = originalAccessor[C.ACCESSOR_COUNT]
	testCount = testAccessor[C.ACCESSOR_COUNT]

	if originalType != testType:
		errStr += f"Accessor <{idHint}> mismatch of required key: {C.ACCESSOR_COUNT}\n\t{originalCount}\n\t{testCount}"

	return errStr

def _compare_type(originalAccessor, testAccessor, idHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.ACCESSOR_TYPE, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	originalType = originalAccessor[C.ACCESSOR_TYPE]
	testType = testAccessor[C.ACCESSOR_TYPE]

	if originalType != testType:
		errStr += f"Accessor <{idHint}> mismatch of required key: {C.ACCESSOR_TYPE}\n\t{originalType}\n\t{testType}"

	return errStr

def _compare_max_float(originalAccessor, testAccessor, idHint, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.ACCESSOR_MAX, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "" or (not C.ACCESSOR_MAX in originalAccessor and not C.ACCESSOR_MAX in testAccessor): # if missing in one, report error and return
		return errStr
	
	originalMax = originalAccessor[C.ACCESSOR_MAX]
	testMax = testAccessor[C.ACCESSOR_MAX]

	errStr += CompareCommon.check_array_size(len(originalMax), originalMax, testMax, idHint, C.ACCESSOR_MAX, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	errStr += CompareCommon.compare_float_array(len(originalMax), originalMax, testMax, idHint, C.ACCESSOR_MAX, C.GLTF_ACCESSOR, floatTolerance)

	return errStr

def _compare_max_other(originalAccessor, testAccessor, idHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.ACCESSOR_MAX, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "" or (not C.ACCESSOR_MAX in originalAccessor and not C.ACCESSOR_MAX in testAccessor): # if missing in one, report error and return
		return errStr
	
	originalMax = originalAccessor[C.ACCESSOR_MAX]
	testMax = testAccessor[C.ACCESSOR_MAX]

	errStr += CompareCommon.check_array_size(len(originalMax), originalMax, testMax, idHint, C.ACCESSOR_MAX, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	errStr += CompareCommon.compare_array(len(originalMax), originalMax, testMax, idHint, C.ACCESSOR_MAX, C.GLTF_ACCESSOR)

	return errStr

def _compare_min_float(originalAccessor, testAccessor, idHint, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.ACCESSOR_MIN, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "" or (not C.ACCESSOR_MIN in originalAccessor and not C.ACCESSOR_MIN in testAccessor): # if missing in one, report error and return
		return errStr
	
	originalMax = originalAccessor[C.ACCESSOR_MIN]
	testMax = testAccessor[C.ACCESSOR_MIN]

	errStr += CompareCommon.check_array_size(len(originalMax), originalMax, testMax, idHint, C.ACCESSOR_MIN, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	errStr += CompareCommon.compare_float_array(len(originalMax), originalMax, testMax, idHint, C.ACCESSOR_MIN, C.GLTF_ACCESSOR, floatTolerance)

	return errStr

def _compare_min_other(originalAccessor, testAccessor, idHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.ACCESSOR_MIN, originalAccessor, testAccessor, idHint, C.GLTF_ACCESSOR)
	if errStr != "" or (not C.ACCESSOR_MIN in originalAccessor and not C.ACCESSOR_MIN in testAccessor): # if missing in one, report error and return
		return errStr
	
	originalMin = originalAccessor[C.ACCESSOR_MIN]
	testMin = testAccessor[C.ACCESSOR_MIN]

	errStr += CompareCommon.check_array_size(len(originalMin), originalMin, testMin, idHint, C.ACCESSOR_MIN, C.GLTF_ACCESSOR)
	if errStr != "":
		return errStr
	
	errStr += CompareCommon.compare_array(len(originalMin), originalMin, testMin, idHint, C.ACCESSOR_MIN, C.GLTF_ACCESSOR)

	return errStr