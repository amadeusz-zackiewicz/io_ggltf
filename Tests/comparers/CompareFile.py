import json
import os
import struct
import base64
import Constants as C
from . import CompareBuffer
from . import CompareAsset
from . import CompareNode
from . import CompareSkin
from . import CompareMesh
from . import CompareAnimation

floatErrTolerance = 0.01

def compare_files(originalFilePath, testFilePath) -> str:
	"""
		Returns a string with a reason for failure, empty string means pass
	"""

	if not os.path.exists(originalFilePath):
		return f"Original file on path: {originalFilePath} does not exist.\n"
	
	if not os.path.exists(testFilePath):
		return f"Test file on path: {testFilePath} does not exist.\n"
	
	fileExt = os.path.basename(originalFilePath).split(".")[-1]

	if fileExt == "glb":
		return _compare_glb(originalFilePath, testFilePath)
	elif fileExt == "gltf":
		return _compare_gltf(originalFilePath, testFilePath)
	else:
		return f"Invalid file extesion '{fileExt}' in file {originalFilePath}\n"

def _get_internal_chunks_glb(jsonChunks, filePath):
	errStr = ""
	file = open(filePath, "+rb")
	file.seek(8, 0) # skip header
	fileLenght = struct.unpack(C.PACKING_FORMAT_U_INT, file.read(4))[0] + 12 # include header size for easier calculations

	glbInternalBuffers = []

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

	return (errStr, glbInternalBuffers)

def _cache_buffers_glb(gltfJson, internalBuffer, mainFilePath):
	errStr = ""
	buffersCache = []
	buffersDicts = gltfJson.get(C.GLTF_BUFFER, None)
	if buffersDicts == None:
		return (errStr, buffersCache)
	
	for i in range(len(buffersDicts)):
		if CompareBuffer.is_buffer_internal(buffersDicts[i]):
			buffersCache.append(internalBuffer)
		else:
			externalBufferPath = CompareBuffer.get_external_buffer_path(mainFilePath, buffersDicts[i])
			bffrStr, buffer = _get_external_buffer(externalBufferPath, buffersDicts[i][C.BUFFER_BYTE_LENGTH])

			errStr += bffrStr
			buffersCache.append(buffer)

	return (errStr, buffersCache)

def _cache_buffers_gltf(gltfJson, mainFilePath):
	errStr = ""
	buffersCache = []
	buffersDicts = gltfJson.get(C.GLTF_BUFFER, None)
	if buffersDicts == None:
		return (errStr, buffersCache)
	
	for i in range(len(buffersDicts)):
		if CompareBuffer.is_buffer_internal(buffersDicts[i]):
			uri = buffersDicts[i].get(C.BUFFER_URI, "")
			bs64BytesFromURI = uri.replace(C.FILE_INTERNAL_BASE64_PREFIX, "", 1)

			if len(bs64BytesFromURI) > 0:
				buffersCache.append(base64.b64decode(bs64BytesFromURI))
			else:
				errStr += f"Failed to load base64 bytes from buffer.\n"
				buffersCache.append(None)
		else:
			externalBufferPath = CompareBuffer.get_external_buffer_path(mainFilePath, buffersDicts[i])
			bffrStr, buffer = _get_external_buffer(externalBufferPath, buffersDicts[i][C.BUFFER_BYTE_LENGTH])

			errStr += bffrStr
			buffersCache.append(buffer)

	return (errStr, buffersCache)


def _get_external_buffer(filePath, bufferLenght):
	errStr = ""

	if not os.path.exists(filePath):
			errStr += f"Error retreiving external buffer at path: {filePath}\n"
			return (errStr, None)

	bufferFile = open(filePath, "+rb")
	buffer = bufferFile.read(bufferLenght)
	bufferFile.close()

	return (errStr, buffer)

def _compare_glb(originalFilePath, testFilePath) -> str:
	errorStr = ""

	originalGltf = []
	testGltf = []

	originalBuffersCache = []
	testBuffersCache = []

	originalBufferLoadStr, originalBufferChunks = _get_internal_chunks_glb(originalGltf, originalFilePath)
	testBufferLoadStr, testBufferChunks = _get_internal_chunks_glb(testGltf, testFilePath)

	errorStr += originalBufferLoadStr
	errorStr += testBufferLoadStr

	if len(originalGltf) != 1:
		errorStr += f"Incorrect amount of JSON chunks within original file: ({len(originalGltf)})\n"
	else:
		originalGltf = json.loads(originalGltf[0])
	if len(testGltf) != 1:
		errorStr += f"Incorrect amount of JSON chunks within test file: ({len(testGltf)})\n"
	else:
		testGltf = json.loads(testGltf[0])

	if len(originalBufferChunks) > 1:
		errorStr += f"Incorrect amount of BIN chunks within original file: ({len(originalBufferChunks)})\n"
	if len(testBufferChunks) > 1:
		errorStr += f"Incorrect amount of BIN chunks within test file: ({len(testBufferChunks)})\n"

	if len(originalBufferChunks) != len(testBufferChunks):
		errorStr += f"Mismatch of BIN chunks between original and test file:\n\t{len(originalBufferChunks)}\n\t{len(testBufferChunks)}\n"


	if errorStr != "":
		errorStr += "Aborting further testing"
		return errorStr

	if len(originalBufferChunks) == 0:
		originalBufferLoadStr, originalBuffersCache = _cache_buffers_glb(originalGltf, None, originalFilePath)
		testBufferLoadStr, testBuffersCache = _cache_buffers_glb(testGltf, None, testFilePath)
		errorStr += originalBufferLoadStr
		errorStr += testBufferLoadStr
	else:
		originalBufferLoadStr, originalBuffersCache = _cache_buffers_glb(originalGltf, originalBufferChunks[0], originalFilePath)
		testBufferLoadStr, testBuffersCache = _cache_buffers_glb(testGltf, testBufferChunks[0], testFilePath)
		errorStr += originalBufferLoadStr
		errorStr += testBufferLoadStr

	if len(originalBuffersCache) != len(testBuffersCache):
		errorStr += f"Mismatch of buffers count between files: {len(originalBuffersCache)} vs {len(testBuffersCache)}\n"

	if errorStr != "":
		errorStr += "Aborting further testing"
		return errorStr

	errorStr += _do_comparisons(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatErrTolerance)

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

	originalBufferLoadStr, originalBuffersCache = _cache_buffers_gltf(originalGltf, originalFilePath)
	testBufferLoadStr, testBuffersCache = _cache_buffers_gltf(testGltf, testFilePath)

	errorStr += originalBufferLoadStr
	errorStr += testBufferLoadStr

	if len(originalBuffersCache) != len(testBuffersCache):
		errorStr += f"Mismatch of buffers count between files: {len(originalBuffersCache)} vs {len(testBuffersCache)}\n"

	if errorStr != "":
		errorStr += "Aborting further testing.\n"
		return errorStr

	errorStr += _do_comparisons(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatErrTolerance)

	return errorStr

def _do_comparisons(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatErrTolerance) -> str:
	errorStr = ""

	errorStr += _compare_asset(originalGltf, testGltf)
	errorStr += _compare_nodes(originalGltf, testGltf)
	errorStr += _compare_skins(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatErrTolerance)
	errorStr += _compare_meshes(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatErrTolerance)
	errorStr += _compare_animations(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatErrTolerance)

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
	
	if not C.GLTF_SKIN in originalGltf:
		errStr += f"No {C.GLTF_SKIN} found in original file.\n"
	if not C.GLTF_SKIN in testGltf:
		errStr += f"No {C.GLTF_SKIN} found in test file.\n"

	if errStr != "": # if nodes are missing from only 1 file, then skip comparison
		return errStr
	
	errStr += CompareSkin.compare_skins(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance)

	return errStr

def _compare_meshes(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance) -> str:
	errStr = ""

	if not C.GLTF_MESH in originalGltf and not C.GLTF_MESH in testGltf:
		return ""
	
	if not C.GLTF_MESH in originalGltf:
		errStr += f"No {C.GLTF_MESH} found in original file.\n"
	if not C.GLTF_MESH in testGltf:
		errStr += f"No {C.GLTF_MESH} found in test file.\n"

	if errStr != "": # if nodes are missing from only 1 file, then skip comparison
		return errStr
	
	errStr += CompareMesh.compare_meshes(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance)

	return errStr

def _compare_animations(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance) -> str:
	errStr = ""

	if not C.GLTF_ANIMATION in originalGltf and not C.GLTF_ANIMATION in testGltf:
		return ""
	
	if not C.GLTF_ANIMATION in originalGltf:
		errStr += f"No {C.GLTF_ANIMATION} found in original file.\n"
	if not C.GLTF_ANIMATION in testGltf:
		errStr += f"No {C.GLTF_ANIMATION} found in test file.\n"

	if errStr != "": # if nodes are missing from only 1 file, then skip comparison
		return errStr
	
	errStr += CompareAnimation.compare_animations(originalGltf, testGltf, originalBuffers, testBuffers, floatTolerance)

	return errStr