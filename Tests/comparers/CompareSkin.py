import Constants as C
from . import CompareCommon
from . import CompareAccessor

def compare_skins(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance) -> str:
	errStr = ""
	
	originalSkins = originalGltf[C.GLTF_SKIN]
	testSkins = testGltf[C.GLTF_SKIN]

	if len(originalSkins) != len(testSkins):
		return f"Skin count mismatch:\n\t{len(originalSkins)} vs {len(testSkins)}\n"
	
	i = 0

	for i in range(len(originalSkins)):
		skinName = originalSkins[i].get(C.SKIN_NAME, str(i))
		errStr += compare_skin(originalSkins[i], testSkins[i], originalBuffers, testBuffers, floatTolerance, skinName, originalGltf, testGltf)
		i += 1

	return errStr

def compare_skin(originalSkin, testSkin, originalBuffers, testBuffers, floatTolerance, idHint, originalGltf, testGltf) -> str:
	errStr = ""

	errStr += CompareCommon.compare_name(originalSkin, testSkin, C.GLTF_SKIN, idHint)
	skinName = originalSkin.get(C.SKIN_NAME, idHint)
	errStr += _compare_skeleton(originalSkin, testSkin, skinName)
	errStr += _compare_joints(originalSkin, testSkin, skinName)
	errStr += _compare_inverse_binds(originalSkin, testSkin, originalBuffers, testBuffers, floatTolerance, idHint, originalGltf, testGltf)

	return errStr

def _compare_skeleton(originalSkin, testSkin, nameHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.SKIN_SKELETON, originalSkin, testSkin, nameHint, C.GLTF_SKIN)
	if errStr != "" or (not C.SKIN_SKELETON in originalSkin and not C.SKIN_SKELETON in testSkin): # if missing in one, report error and return
		return errStr
	
	if originalSkin[C.SKIN_SKELETON] != testSkin[C.SKIN_SKELETON]:
		errStr += f"Skin <{nameHint}> has mismatched skeleton IDs:\n\t{originalSkin[C.SKIN_SKELETON]} vs {testSkin[C.SKIN_SKELETON]}\n"

	return errStr

def _compare_joints(originalNode, testNode, nameHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.SKIN_JOINTS, originalNode, testNode, nameHint, C.GLTF_SKIN)
	if errStr != "" or (not C.SKIN_JOINTS in originalNode and not C.SKIN_JOINTS in testNode): # if missing in one, report error and return
		return errStr
	
	originalChildren = originalNode[C.SKIN_JOINTS]
	testChildren = testNode[C.SKIN_JOINTS]

	if originalChildren != testChildren:
		errStr += f"Skin <{nameHint}> has mismatched joint IDs:\n\t{originalNode[C.SKIN_JOINTS]}\n\t{testNode[C.SKIN_JOINTS]}\n"

	return errStr

def _compare_inverse_binds(originalSkin, testSkin, originalBuffers, testBuffers, floatTolerance, idHint, originalGltf, testGltf) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.SKIN_INVERSE_BIND_MATRICES, originalSkin, testSkin, idHint, C.GLTF_SKIN)
	if errStr != "" or (not C.SKIN_INVERSE_BIND_MATRICES in originalSkin and not C.SKIN_INVERSE_BIND_MATRICES in testSkin): # if missing in one, report error and return
		return errStr

	originalAccessors = CompareAccessor.get_accessors(originalGltf)
	testAccessors = CompareAccessor.get_accessors(testGltf)

	originalAccessorID = originalSkin[C.SKIN_INVERSE_BIND_MATRICES]
	testAccessorID = testSkin[C.SKIN_INVERSE_BIND_MATRICES]

	originalAccessor = {}
	testAccessor = {}

	if originalAccessorID < len(originalAccessors):
		originalAccessor = originalAccessors[originalAccessorID]
	else:
		errStr += f"Original:skin[{idHint}].inverseBinds is out of bounds: ({originalAccessorID}/{len(originalAccessors)})\n"
	if testAccessorID < len(testAccessors):
		testAccessor = testAccessors[testAccessorID]
	else:
		errStr += f"Test:skin[{idHint}].inverseBinds is out of bounds: ({testAccessorID}/{len(testAccessors)})\n"

	if errStr != "":
		return errStr

	errStr += CompareAccessor.compare_accessor(originalAccessor, testAccessor, originalBuffers, testBuffers, floatTolerance, originalGltf, testGltf, f"skin[{idHint}].inverseBinds")

	return errStr
