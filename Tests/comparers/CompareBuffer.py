import Constants as C


def is_buffer_internal(bufferDict) -> bool:
	if not C.BUFFER_URI in bufferDict or bufferDict[C.BUFFER_URI].find(C.FILE_INTERNAL_BASE64_PREFIX, 0, len(C.FILE_INTERNAL_BASE64_PREFIX) + 4) > -1:
		return True
	else:
		return False