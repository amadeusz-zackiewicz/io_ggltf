import Constants as C


def compare_name(originalDict, testDict, typeHint, id) -> str:
	errStr = ""
	
	if not C.__VAR_NAME in originalDict and not C.__VAR_NAME in testDict: # if missing in both then skip
		return ""
	
	if not C.__VAR_NAME in originalDict:
		errStr += f"{typeHint.capitalize()} <{id}> is missing a name in original file.\n"
	if not C.__VAR_NAME in testDict:
		errStr += f"{typeHint.capitalize()} <{id}> is missing a name in test file.\n"

	if errStr != "": # if missing in one, report error and skip
		return errStr
	
	if originalDict[C.__VAR_NAME] != testDict[C.__VAR_NAME]:
		errStr += f"Node <{id}> name mismatch:\n\t{originalDict[C.__VAR_NAME]} vs {testDict[C.__VAR_NAME]}.\n"

	return errStr

def check_key_exists(key, originalDict, testDict, nameHint, typeHint) -> str:
	errStr = ""

	if not key in originalDict and not key in testDict: # if missing in both then skip
		return ""
	
	if not key in originalDict:
		errStr += f"Type: {typeHint.capitalize()} <{nameHint}> is missing a {key} in original file.\n"
	if not key in testDict:
		errStr += f"Type: {typeHint.capitalize()} <{nameHint}> is missing a {key} in test file.\n"	

	return errStr