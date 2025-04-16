import Constants as C
from . import CompareCommon

matrixLenght = 16
translationLength = 3
rotationLenght = 4
scaleLenght = 3

def compare_nodes(originalGltf, testGltf, floatTolerance) -> str:
	errStr = ""
	
	originalNodes = originalGltf[C.GLTF_NODE]
	testNodes = testGltf[C.GLTF_NODE]

	if len(originalNodes) != len(testNodes):
		return f"Node count mismatch:\n\t{len(originalNodes)} vs {len(testNodes)}\n"
	
	i = 0

	while i < len(originalNodes):
		errStr += CompareCommon.compare_name(originalNodes[i], testNodes[i], C.GLTF_NODE, i)
		nodeName = originalNodes[i].get(C.NODE_NAME, i)
		errStr += _compare_matrix(originalNodes[i], testNodes[i], nodeName, floatTolerance)
		errStr += _compare_translation(originalNodes[i], testNodes[i], nodeName, floatTolerance)
		errStr += _compare_rotation(originalNodes[i], testNodes[i], nodeName, floatTolerance)
		errStr += _compare_scale(originalNodes[i], testNodes[i], nodeName, floatTolerance)
		errStr += _compare_camera(originalNodes[i], testNodes[i], nodeName)
		errStr += _compare_mesh(originalNodes[i], testNodes[i], nodeName)
		errStr += _compare_skin(originalNodes[i], testNodes[i], nodeName)
		errStr += _compare_children(originalNodes[i], testNodes[i], nodeName)
		errStr += _compare_weights(originalNodes[i], testNodes[i], nodeName, floatTolerance)
		i += 1

	return errStr
	
def _compare_matrix(originalNode, testNode, nodeName, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_MATRIX, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_MATRIX in originalNode and not C.NODE_MATRIX in testNode): # if missing in one, report error and return
		return errStr

	originalMatrix = originalNode[C.NODE_MATRIX]
	testMatrix = testNode[C.NODE_MATRIX]

	errStr += CompareCommon.check_array_size(matrixLenght, originalMatrix, testMatrix, nodeName, C.NODE_MATRIX, C.GLTF_NODE)
	if errStr != "": # if matrix size has mismatch then return
		return errStr
	
	errStr += CompareCommon.compare_float_array(matrixLenght, originalMatrix, testMatrix, nodeName, C.NODE_MATRIX, C.GLTF_NODE, floatTolerance)

	return errStr

def _compare_translation(originalNode, testNode, nodeName, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_TRANSLATION, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_TRANSLATION in originalNode and not C.NODE_TRANSLATION in testNode): # if missing in one, report error and return
		return errStr
	
	originalTranslation = originalNode[C.NODE_TRANSLATION]
	testTranslation = testNode[C.NODE_TRANSLATION]

	errStr += CompareCommon.check_array_size(translationLength, originalTranslation, testTranslation, nodeName, C.NODE_TRANSLATION, C.GLTF_NODE)
	if errStr != "": # if translation size has mismatch then return
		return errStr
	
	errStr += CompareCommon.compare_float_array(translationLength, originalTranslation, testTranslation, nodeName, C.NODE_TRANSLATION, C.GLTF_NODE, floatTolerance)

	return errStr

def _compare_rotation(originalNode, testNode, nodeName, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_ROTATION, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_ROTATION in originalNode and not C.NODE_ROTATION in testNode): # if missing in one, report error and return
		return errStr
	
	originalRotation = originalNode[C.NODE_ROTATION]
	testRotation = testNode[C.NODE_ROTATION]

	errStr += CompareCommon.check_array_size(rotationLenght, originalRotation, testRotation, nodeName, C.NODE_ROTATION, C.GLTF_NODE)
	if errStr != "": # if rotation size has mismatch then return
		return errStr
	
	errStr += CompareCommon.compare_float_array(rotationLenght, originalRotation, testRotation, nodeName, C.NODE_ROTATION, C.GLTF_NODE, floatTolerance)

	return errStr

def _compare_scale(originalNode, testNode, nodeName, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_SCALE, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_SCALE in originalNode and not C.NODE_SCALE in testNode): # if missing in one, report error and return
		return errStr
	
	originalScale = originalNode[C.NODE_SCALE]
	testScale = testNode[C.NODE_SCALE]

	errStr += CompareCommon.check_array_size(scaleLenght, originalScale, testScale, nodeName, C.NODE_SCALE, C.GLTF_NODE)
	if errStr != "": # if scale size has mismatch then return
		return errStr
	
	errStr += CompareCommon.compare_float_array(scaleLenght, originalScale, testScale, nodeName, C.NODE_SCALE, C.GLTF_NODE, floatTolerance)

	return errStr

def _compare_camera(originalNode, testNode, nodeName) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_CAMERA, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_CAMERA in originalNode and not C.NODE_CAMERA in testNode): # if missing in one, report error and return
		return errStr
	
	if originalNode[C.NODE_CAMERA] != testNode[C.NODE_CAMERA]:
		errStr += f"Node <{nodeName}> has mismatched camera IDs:\n\t{originalNode[C.NODE_CAMERA]} vs {testNode[C.NODE_CAMERA]}"

	return errStr

def _compare_mesh(originalNode, testNode, nodeName) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_MESH, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_MESH in originalNode and not C.NODE_MESH in testNode): # if missing in one, report error and return
		return errStr
	
	if originalNode[C.NODE_MESH] != testNode[C.NODE_MESH]:
		errStr += f"Node <{nodeName}> has mismatched mesh IDs:\n\t{originalNode[C.NODE_MESH]} vs {testNode[C.NODE_MESH]}"

	return errStr

def _compare_skin(originalNode, testNode, nodeName) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_SKIN, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_SKIN in originalNode and not C.NODE_SKIN in testNode): # if missing in one, report error and return
		return errStr
	
	if originalNode[C.NODE_SKIN] != testNode[C.NODE_SKIN]:
		errStr += f"Node <{nodeName}> has mismatched skin IDs:\n\t{originalNode[C.NODE_SKIN]} vs {testNode[C.NODE_SKIN]}"

	return errStr

def _compare_children(originalNode, testNode, nodeName) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_CHILDREN, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_CHILDREN in originalNode and not C.NODE_CHILDREN in testNode): # if missing in one, report error and return
		return errStr
	
	originalChildren = originalNode[C.NODE_CHILDREN]
	testChildren = testNode[C.NODE_CHILDREN]

	originalChildren.sort()
	testChildren.sort() # prevent mismatched if children are in the exact order

	if originalChildren != testChildren:
		errStr += f"Node <{nodeName}> has mismatched children IDs:\n\t{originalNode[C.NODE_SKIN]}\n\t{testNode[C.NODE_SKIN]}"

	return errStr

def _compare_weights(originalNode, testNode, nodeName, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.NODE_WEIGHTS, originalNode, testNode, nodeName, C.GLTF_NODE)
	if errStr != "" or (not C.NODE_WEIGHTS in originalNode and not C.NODE_WEIGHTS in testNode): # if missing in one, report error and return
		return errStr
	
	originalWeights = originalNode[C.NODE_WEIGHTS]
	testWeights = testNode[C.NODE_WEIGHTS]

	errStr += CompareCommon.check_array_size(len(originalWeights), originalWeights, testWeights, nodeName, C.NODE_WEIGHTS, C.GLTF_NODE)
	if errStr != "": # if rotation size has mismatch then return
		return errStr
	
	errStr += CompareCommon.compare_float_array(len(originalWeights), originalWeights, testWeights, nodeName, C.NODE_WEIGHTS, C.GLTF_NODE, floatTolerance)

	return errStr