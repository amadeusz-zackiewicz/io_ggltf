import Constants as C

def compare_asset(originalAsset, testAsset) -> str:

	errorStr = ""

	errorStr += _compare_keys_optional(C.ASSET_COPYRIGHT, originalAsset, testAsset)
	errorStr += _compare_keys_optional(C.ASSET_GENERATOR, originalAsset, testAsset)

	if C.ASSET_VERSION in originalAsset:
		if C.ASSET_VERSION in testAsset:
			if originalAsset[C.ASSET_VERSION] != testAsset[C.ASSET_VERSION]:
				errorStr += f"Required key: '{C.ASSET_VERSION}' mismatch:\n\t\tOriginal: {originalAsset[C.ASSET_VERSION]}\n\t\tTest: {testAsset[C.ASSET_VERSION]}"
		else:
			errorStr += f"Asset file is missing a Required '{C.ASSET_VERSION}' key.\n"
	else:
		errorStr += f"Original file is missing a Required '{C.ASSET_VERSION}' key.\n"

	errorStr += _compare_keys_optional(C.ASSET_MIN_VERSION, originalAsset, testAsset)

	# TODO: extensions and extras not supported at the moment

	return errorStr

def _compare_keys_optional(key, originalAsset, testAsset) -> str:
	if key in originalAsset:
		if not key in testAsset:
			return f"'{key}' found in original but not test file.\n"
		else:
			if originalAsset[key] != testAsset[key]:
				return f"'{key}' mismatch between original and test:\n\t\tOriginal - {originalAsset[key]}\n\t\tTest - {testAsset[key]}"
	return ""