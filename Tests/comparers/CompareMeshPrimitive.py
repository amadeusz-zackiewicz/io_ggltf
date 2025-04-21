import Constants as C
from . import CompareCommon
from . import CompareAccessor

def compare_mesh_primitive(originalPrimitive, testPrimitive, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, ownerHint) -> str:
	errStr = ""

	errStr += _compare_mode(originalPrimitive, testPrimitive, ownerHint)
	errStr += _compare_indices(originalPrimitive, testPrimitive, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, ownerHint)
	errStr += _compare_attributes(originalPrimitive, testPrimitive, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, ownerHint)

	return errStr

def _compare_mode(originalPrimitive, testPrimitive, owneHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.MESH_PRIMITIVE_MODE, originalPrimitive, testPrimitive, owneHint, f"{C.GLTF_MESH}.primitive")
	if errStr != "" or (not C.MESH_PRIMITIVE_MODE in originalPrimitive and not C.MESH_PRIMITIVE_MODE in testPrimitive): # if missing in one, report error and return
		return errStr
	
	if originalPrimitive[C.MESH_PRIMITIVE_MODE] != testPrimitive[C.MESH_PRIMITIVE_MODE]:
		errStr += f"<{owneHint}> has mismatched modes:\n\t{originalPrimitive[C.MESH_PRIMITIVE_MODE]} vs {testPrimitive[C.MESH_PRIMITIVE_MODE]}\n"

	return errStr

def _compare_indices(originalPrimitive, testPrimitive, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, ownerHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.MESH_PRIMITIVE_INDICES, originalPrimitive, testPrimitive, ownerHint, f"{C.GLTF_MESH}.primitive")
	if errStr != "" or (not C.MESH_PRIMITIVE_INDICES in originalPrimitive and not C.MESH_PRIMITIVE_INDICES in testPrimitive): # if missing in one, report error and return
		return errStr
	
	originalAccessors = CompareAccessor.get_accessors(originalGltf)
	testAccessors = CompareAccessor.get_accessors(testGltf)

	originalAccessorID = originalPrimitive[C.MESH_PRIMITIVE_INDICES]
	testAccessorID = testPrimitive[C.MESH_PRIMITIVE_INDICES]

	originalAccessor = {}
	testAccessor = {}

	if originalAccessorID < len(originalAccessors):
		originalAccessor = originalAccessors[originalAccessorID]
	else:
		errStr += f"Original:[{ownerHint}].{C.MESH_PRIMITIVE_INDICES} is out of bounds: ({originalAccessorID}/{len(originalAccessors)})\n"
	if testAccessorID < len(testAccessors):
		testAccessor = testAccessors[testAccessorID]
	else:
		errStr += f"Test:[{ownerHint}].{C.MESH_PRIMITIVE_INDICES} is out of bounds: ({testAccessorID}/{len(testAccessors)})\n"

	if errStr != "":
		return errStr

	errStr += CompareAccessor.compare_accessor(originalAccessor, testAccessor, originalBuffersCache, testBuffersCache, floatTolerance, originalGltf, testGltf, f"{ownerHint}.indices")

	return errStr

def _compare_attributes(originalPrimitive, testPrimitive, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, ownerHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.MESH_PRIMITIVE_ATTRIBUTES, originalPrimitive, testPrimitive, ownerHint, C.MESH_PRIMITIVES)
	if errStr != "":
		return errStr
	
	originalAttributes = originalPrimitive[C.MESH_PRIMITIVE_ATTRIBUTES]
	testAttributes = testPrimitive[C.MESH_PRIMITIVE_ATTRIBUTES]

	if len(originalAttributes) != len(testAttributes):
		errStr += f"Mesh[{ownerHint}] has mismatched attributes size:\n\t({len(originalAttributes)} - {originalAttributes}\n\t({len(testAttributes)}) - {testAttributes})\n"

	if errStr != "":
		return errStr
	
	originalAttributesKeys = list(originalAttributes.keys())
	testAttributesKeys = list(testAttributes.keys())
	originalAttributesKeys.sort()
	testAttributesKeys.sort()

	errStr += CompareCommon.compare_array(len(originalAttributesKeys), originalAttributesKeys, testAttributesKeys, ownerHint, C.MESH_PRIMITIVE_ATTRIBUTES, C.MESH_PRIMITIVES)

	if errStr != "":
		return errStr
	
	originalAccessors = CompareAccessor.get_accessors(originalGltf)
	testAccessors = CompareAccessor.get_accessors(testGltf)

	if errStr != "":
		return errStr
	
	for attribute in originalAttributesKeys:
		originalAttrAccessorID = originalAttributes[attribute]
		testAttrAccessorID = testAttributes[attribute]

		originalAccessor = {}
		testAccessor = {}

		boundsErr = ""

		if originalAttrAccessorID < len(originalAccessors):
			originalAccessor = originalAccessors[originalAttrAccessorID]
		else:
			boundsErr += f"Original:[{ownerHint}].{C.MESH_PRIMITIVE_INDICES} is out of bounds: ({originalAttrAccessorID}/{len(originalAccessors)})\n"
		if testAttrAccessorID < len(testAccessors):
			testAccessor = testAccessors[testAttrAccessorID]
		else:
			boundsErr += f"Test:[{ownerHint}].{C.MESH_PRIMITIVE_INDICES} is out of bounds: ({testAttrAccessorID}/{len(testAccessors)})\n"

		if boundsErr != "":
			errStr += boundsErr
			continue
		
		errStr += CompareAccessor.compare_accessor(originalAccessor, testAccessor, originalBuffersCache, testBuffersCache, floatTolerance, originalGltf, testGltf, f"{ownerHint}.attributes[{attribute}]")

	return errStr