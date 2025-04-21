import Constants as C
from . import CompareCommon
from . import CompareMeshPrimitive
from . import CompareAccessor

def compare_meshes(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatTolerance) -> str:
	errStr = ""
	
	originalMeshes = originalGltf[C.GLTF_MESH]
	testMeshes = testGltf[C.GLTF_MESH]

	if len(originalMeshes) != len(testMeshes):
		return f"Mesh count mismatch:\n\t{len(originalMeshes)} vs {len(testMeshes)}\n"

	for i in range(len(originalMeshes)):
		meshName = originalMeshes[i].get(C.MESH_NAME, i)
		errStr += compare_mesh(originalMeshes[i], testMeshes[i], originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, f"mesh[{meshName}]")

	return errStr

def compare_mesh(originalMesh, testMesh, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, idHint) -> str:
	errStr = ""

	idHint = originalMesh.get(C.MESH_NAME, idHint)

	errStr += _compare_weights(originalMesh, testMesh, idHint, floatTolerance)
	errStr += _compare_primitives(originalMesh, testMesh, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, idHint)

	return errStr

def _compare_weights(originalMesh, testMesh, idHint, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_key_exists(C.MESH_WEIGHTS, originalMesh, testMesh, idHint, C.GLTF_MESH)
	if errStr != "" or (not C.MESH_WEIGHTS in originalMesh and not C.NODE_WEIGHTS in testMesh): # if missing in one, report error and return
		return errStr
	
	originalWeights = originalMesh[C.MESH_WEIGHTS]
	testWeights = testMesh[C.MESH_WEIGHTS]

	errStr += CompareCommon.check_array_size(len(originalWeights), originalWeights, testWeights, idHint, C.MESH_WEIGHTS, C.GLTF_MESH)
	if errStr != "": # if rotation size has mismatch then return
		return errStr
	
	errStr += CompareCommon.compare_float_array(len(originalWeights), originalWeights, testWeights, idHint, C.MESH_WEIGHTS, C.GLTF_MESH, floatTolerance)

	return errStr

def _compare_primitives(originalMesh, testMesh, originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, ownerHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.MESH_PRIMITIVES, originalMesh, testMesh, ownerHint, C.GLTF_MESH)
	if errStr != "":
		return errStr
	
	originalPrimitives = originalMesh[C.MESH_PRIMITIVES]
	testPrimitives = testMesh[C.MESH_PRIMITIVES]

	if len(originalPrimitives) != len(testPrimitives):
		errStr += f"Mesh[{ownerHint}] has mismatched primitives size:\n\t({len(originalPrimitives)} - {originalPrimitives}\n\t({len(testPrimitives)}) - {testPrimitives})\n"

	if errStr != "":
		return errStr
	
	for i in range(len(originalPrimitives)):
		errStr += CompareMeshPrimitive.compare_mesh_primitive(originalPrimitives[i], testPrimitives[i], originalBuffersCache, testBuffersCache, originalGltf, testGltf, floatTolerance, f"{ownerHint}.primitives[{i}]")

	return errStr