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

def check_required_key(key, originalDict, testDict, nameHint, typeHint) -> str:
	errStr = ""

	if not key in originalDict:
		errStr += f"<Type:{typeHint.capitalize()}> <{nameHint}> is missing a required key {key} in original file.\n"
	if not key in testDict:
		errStr += f"<Type: {typeHint.capitalize()}> <{nameHint}> is missing a required key {key} in test file.\n"	

	return errStr

def check_array_size(expectedSize, originalArray, testArray, name, keyHint, typeHint) -> str:
	errStr = ""

	if len(originalArray) != expectedSize:
		errStr += f"{typeHint.capitalize()} <{name}> has incorrect {keyHint} size in original file: {len(originalArray)}.\n"
	if len(testArray) != expectedSize:
		errStr += f"{typeHint.capitalize()} <{name}> has incorrect {keyHint} size in test file: {len(testArray)}.\n"

	return errStr

def compare_float_array(size, originalArray, testArray, name, keyHint, typeHint, floatTolerance) -> str:
	errStr = ""

	i = 0
	while i < size:
		originalValue = originalArray[i]
		testValue = testArray[i]

		diff = abs(originalValue - testValue)

		if diff > floatTolerance:
			errStr += f"{keyHint} mismatch in {typeHint.capitalize()} <{name}>:\n\t{originalArray}\n\t{testArray}\n"
			break

		i += 1	

	return errStr

def compare_array(size, originalArray, testArray, name, keyHint, typeHint) -> str:
	errStr = ""

	i = 0
	while i < size:
		if originalArray[i] != testArray[i]:
			errStr += f"{keyHint} mismatch in {typeHint.capitalize()} <{name}>:\n\t{originalArray}\n\t{testArray}\n"
			break
		i += 1

	return errStr

def is_component_type_floaty(componentType) -> bool:
	return componentType == C.PACKING_FORMAT_FLOAT or componentType == C.PACKING_FORMAT_DOUBLE