import json
import os
import struct
import Constants as C
from . import CompareBuffer as CompareBuffer
from . import CompareAsset as CompareAsset
from . import CompareNode as CompareNode

floatErrTolerance = 0.01

def compare_files(originalFilePath, testFilePath) -> str:
	"""
		Returns a string with a reason for failure, empty string means pass
	"""

	if not os.path.exists(originalFilePath):
		return f"Original file on path: {originalFilePath} does not exist."
	
	if not os.path.exists(testFilePath):
		return f"Test file on path: {testFilePath} does not exist."
	
	fileExt = os.path.basename(originalFilePath).split(".")[-1]

	if fileExt == "glb":
		return _compare_glb(originalFilePath, testFilePath)
	elif fileExt == "gltf":
		return _compare_gltf(originalFilePath, testFilePath)
	else:
		return f"Invalid file extesion '{fileExt}' in file {originalFilePath}"

def _extract_json_from_glb(filePath) -> str:
	file = open(filePath, "+rb")
	file.seek(12, 0)
	jsonChunkLength = struct.unpack("i", file.read(4))[0]
	file.seek(20, 0)
	gltfStr = str(file.read(jsonChunkLength).decode("utf-8"))
	file.close()

	return json.loads(gltfStr)

def _compare_glb(originalFilePath, testFilePath) -> str:
	errorStr = ""

	originalGltf = _extract_json_from_glb(originalFilePath)
	testGltf = _extract_json_from_glb(testFilePath)

	errorStr += _compare_asset(originalGltf, testGltf)
	errorStr += _compare_nodes(originalGltf, testGltf)

	return errorStr

def _compare_gltf(originalFilePath, testFilePath) -> str:
	errorStr = ""

	originalFile = open(originalFilePath, "+r")
	originalGltf = json.load(originalFile)
	originalFile.close()

	testFile = open(testFilePath, "+r")
	testGltf = json.load(testFile)
	testFile.close()

	del originalFile
	del testFile

	errorStr += _compare_asset(originalGltf, testGltf)
	errorStr += _compare_nodes(originalGltf, testGltf)

	return errorStr

def _compare_asset(originalGltf, testGltf) -> str: # required key
	assetErr = ""

	if C.GLTF_ASSET in originalGltf:
		if not C.GLTF_ASSET in testGltf:
			assetErr += f"Required '{C.GLTF_ASSET}' key missing from test file.\n"
		else:
			assetErr += CompareAsset.compare_asset(originalGltf[C.GLTF_ASSET], testGltf[C.GLTF_ASSET])
	else:
		assetErr += f"Required '{C.GLTF_ASSET}' key missin from original file.\n"

	if assetErr != "":
		assetErr = "Asset:\n" + assetErr

	return assetErr

def _compare_nodes(originalGltf, testGltf) -> str:
	errStr = ""

	if not C.GLTF_NODE in originalGltf and not C.GLTF_NODE in testGltf: # if there are no nodes then skip
		return ""
	
	if not C.GLTF_NODE in originalGltf:
		errStr += f"\tNo {C.GLTF_NODE} found in original file.\n"
	if not C.GLTF_NODE in testGltf:
		errStr += f"\tNo {C.GLTF_NODE} found in test file.\n"

	if errStr != "": # if nodes are missing from only 1 file, then skip comparison
		return errStr
	
	errStr += CompareNode.compare_nodes(originalGltf, testGltf, floatErrTolerance)

	return errStr