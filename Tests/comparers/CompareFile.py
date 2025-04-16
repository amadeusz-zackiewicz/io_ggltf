import json
import os
import struct
import base64
import Constants as C
from . import CompareBuffer
from . import CompareAsset
from . import CompareNode
from . import CompareSkin

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

def _get_internal_chunks_glb(jsonChunks, glbInternalBuffers, filePath) -> str:
	errStr = ""
	file = open(filePath, "+rb")
	file.seek(8, 0) # skip header
	fileLenght = struct.unpack(C.PACKING_FORMAT_U_INT, file.read(4))[0] + 12 # include header size for easier calculations

	while True:
		if file.tell() >= fileLenght:
			break

		chunkLengthBytes = file.read(4)
		if len(chunkLengthBytes) < 4:
			break
		chunkTypeBytes = file.read(4)
		if len(chunkTypeBytes) < 4:
			break

		chunkLenght = struct.unpack(C.PACKING_FORMAT_U_INT, chunkLengthBytes)[0]
		chunkType = struct.unpack(C.PACKING_FORMAT_U_INT, chunkTypeBytes)[0]

		if file.tell() >= fileLenght:
			break

		if chunkType == C.FILE_BIN_CHUNK_TYPE_JSON:
			chunkData = file.read(chunkLenght).decode("utf-8")
			jsonChunks.append(chunkData)
		elif chunkType == C.FILE_BIN_CHUNK_TYPE_BIN:
			chunkData = file.read(chunkLenght)
			glbInternalBuffers.append(chunkData)
		else:
			continue # if type is unknown then we skip, some extensions might use custom types

	return errStr

def _get_external_buffers(buffersMap, gltfJson, mainFilePath) -> str:
	errStr = ""

	buffersDicts = gltfJson.get(C.GLTF_BUFFER, None)
	if buffersDicts == None:
		return errStr
	
	for i in range(len(buffersDicts)):
		if CompareBuffer.is_buffer_internal(buffersDicts[i]):
			continue

		bufferURI = buffersDicts[i].get(C.BUFFER_URI, "")

		bufferFilePath = os.path.join(os.path.dirname(mainFilePath), bufferURI)

		if not os.path.exists(bufferFilePath):
			errStr += f"Error retreiving external buffer at path: {bufferFilePath}"
			continue

		bufferFile = open(bufferFilePath, "+rb")
		bufferLenght = buffersDicts[i].get(C.BUFFER_BYTE_LENGTH, os.path.getsize(bufferFilePath))

		buffersMap[bufferURI] = bufferFile.read(bufferLenght)
		bufferFile.close()
	
	return errStr

def _get_internal_buffers_gltf(bufferMap, gltfJson) -> str:
	errStr = ""

	buffersDicts = gltfJson.get(C.GLTF_BUFFER, None)
	if buffersDicts == None:
		return errStr

	for i in range(len(buffersDicts)):
		if not CompareBuffer.is_buffer_internal(buffersDicts[i]):
			continue

		uri = buffersDicts[i].get(C.BUFFER_URI, "")

		if len(uri) > 0:
			bs64BytesFromURI = uri.replace(C.FILE_INTERNAL_BASE64_PREFIX, "", 1)
			bufferMap[i] = base64.b64decode(bs64BytesFromURI)

	return errStr

def _map_glb_internal_buffer(gltfJson) -> int:
	buffersDicts = gltfJson[C.GLTF_BUFFER]

	for i in range(len(buffersDicts)):
		if CompareBuffer.is_buffer_internal(buffersDicts[i]):
			return i

def _compare_glb(originalFilePath, testFilePath) -> str:
	errorStr = ""

	originalGltf = []
	testGltf = []
	originalBuffers = []
	testBuffers = []

	originalBuffersMap = {}
	testBuffersMap = {}

	errorStr += _get_internal_chunks_glb(originalGltf, originalBuffers, originalFilePath)
	errorStr += _get_internal_chunks_glb(testGltf, testBuffers, testFilePath)

	if len(originalGltf) != 1:
		errorStr += f"Incorrect amount of JSON chunks within original file: ({len(originalGltf)})"
	else:
		originalGltf = json.loads(originalGltf[0])
	if len(testGltf) != 1:
		errorStr += f"Incorrect amount of JSON chunks within test file: ({len(testGltf)})"
	else:
		testGltf = json.loads(testGltf[0])

	errorStr += _get_external_buffers(originalBuffersMap, originalGltf, originalFilePath)
	errorStr += _get_external_buffers(testBuffersMap, testGltf, testFilePath)

	if len(originalBuffers) > 1:
		errorStr += f"Incorrect amount of BIN chunks within original file: ({len(originalBuffers)})"
	elif len(originalBuffers) > 0:
		originalBuffersMap[_map_glb_internal_buffer(originalGltf)] = originalBuffers[0]
	if len(testBuffers) > 1:
		errorStr += f"Incorrect amount of BIN chunks within test file: ({len(testBuffers)})"
	elif len(testBuffers) > 0:
		testBuffersMap[_map_glb_internal_buffer(testGltf)] = testBuffers[0]


	if len(originalBuffersMap) != len(testBuffersMap):
		errorStr += f"Mismatch of buffers count between files: {len(originalBuffersMap)} vs {len(testBuffersMap)}"

	if errorStr != "":
		return errorStr

	errorStr += _compare_asset(originalGltf, testGltf)
	errorStr += _compare_nodes(originalGltf, testGltf)
	errorStr += _compare_skins(originalGltf, testGltf, originalBuffersMap, testBuffersMap, floatErrTolerance)

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

	originalBuffersMap = {}
	testBuffersMap = {}

	errorStr += _get_internal_buffers_gltf(originalBuffersMap, originalGltf)
	errorStr += _get_internal_buffers_gltf(testBuffersMap, testGltf)

	errorStr += _get_external_buffers(originalBuffersMap, originalGltf, originalFilePath)
	errorStr += _get_external_buffers(testBuffersMap, testGltf, testFilePath)

	errorStr += _compare_asset(originalGltf, testGltf)
	errorStr += _compare_nodes(originalGltf, testGltf)
	errorStr += _compare_skins(originalGltf, testGltf, originalBuffersMap, testBuffersMap, floatErrTolerance)

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
		errStr += f"No {C.GLTF_NODE} found in original file.\n"
	if not C.GLTF_NODE in testGltf:
		errStr += f"No {C.GLTF_NODE} found in test file.\n"

	if errStr != "": # if nodes are missing from only 1 file, then skip comparison
		return errStr
	
	errStr += CompareNode.compare_nodes(originalGltf, testGltf, floatErrTolerance)

	return errStr

def _compare_skins(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance) -> str:
	errStr = ""

	if not C.GLTF_SKIN in originalGltf and not C.GLTF_SKIN in testGltf:
		return ""
	
	if not C.GLTF_NODE in originalGltf:
		errStr += f"No {C.GLTF_SKIN} found in original file.\n"
	if not C.GLTF_NODE in testGltf:
		errStr += f"No {C.GLTF_SKIN} found in test file.\n"

	if errStr != "": # if nodes are missing from only 1 file, then skip comparison
		return errStr
	
	errStr += CompareSkin.compare_skins(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance)

	return errStr