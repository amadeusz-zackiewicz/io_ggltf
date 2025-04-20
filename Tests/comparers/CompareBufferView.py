import Constants as C
from . import CompareCommon
from . import CompareBuffer

def compare_buffer_view(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatTolerance, componentType, groupingType, originalID, testID, ownerHint) -> str:
	errStr = ""

	originalBufferView = originalGltf[C.GLTF_BUFFER_VIEW][originalID]
	testBufferView = testGltf[C.GLTF_BUFFER_VIEW][testID]

	errStr += _compare_byte_lenght(originalBufferView, testBufferView, ownerHint)
	if errStr != "":
		return
	errStr += _compare_buffer(originalBufferView, testBufferView, originalBuffersCache, testBuffersCache, floatTolerance, groupingType, componentType, ownerHint)

	return errStr

def _compare_byte_lenght(originalBufferView, testBufferView, ownerHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.BUFFER_VIEW_BYTE_LENGTH, originalBufferView, testBufferView, ownerHint, C.GLTF_BUFFER_VIEW)
	if errStr != "":
		return errStr
	
	originalByteLength = originalBufferView[C.BUFFER_VIEW_BYTE_LENGTH]
	testByteLength = testBufferView[C.BUFFER_VIEW_BYTE_LENGTH]

	if originalByteLength != testByteLength:
		errStr += f"BufferView of <{ownerHint}> mismatch of required key: {C.BUFFER_VIEW_BYTE_LENGTH}\n\t{originalByteLength}\n\t{testByteLength}\n"

	return errStr

def _compare_buffer(originalBufferView, testBufferView, originalBuffersCache, testBuffersCache, floatTolerance, groupingType, componentType, ownerHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.BUFFER_VIEW_BUFFER, originalBufferView, testBufferView, ownerHint, C.GLTF_BUFFER_VIEW)
	if errStr != "":
		return errStr
	
	originalBufferID = originalBufferView[C.BUFFER_VIEW_BUFFER]
	testBufferID = testBufferView[C.BUFFER_VIEW_BUFFER]

	if originalBufferID >= len(originalBuffersCache):
		errStr += f"Original:{ownerHint}.accessor.bufferView.buffer is out of bounds: ({originalBufferID}/{len(originalBuffersCache)})\n"
	if testBufferID >= len(testBuffersCache):
		errStr += f"Test:{ownerHint}.accessor.bufferView.buffer is out of bounds: ({testBufferID}/{len(testBuffersCache)})\n"

	if errStr != "":
		return errStr
	
	originalBufferByteOffset = originalBufferView.get(C.BUFFER_VIEW_BYTE_OFFSET, 0)
	testBufferByteOffset = testBufferView.get(C.BUFFER_VIEW_BYTE_OFFSET, 0)
	
	errStr += CompareBuffer.compare_buffer(originalBuffersCache[originalBufferID], testBuffersCache[testBufferID], originalBufferByteOffset, testBufferByteOffset, originalBufferView[C.BUFFER_BYTE_LENGTH], floatTolerance, componentType, groupingType, ownerHint)

	return errStr