import Constants as C
from . import CompareCommon
from . import CompareAccessor

def compare_animations(originalGltf, testGltf, originalBuffersCache, testBuffersCache, floatTolerance) -> str:
	errStr = ""

	originalAnimations = originalGltf[C.GLTF_ANIMATION]
	testAnimations = testGltf[C.GLTF_ANIMATION]

	if len(originalAnimations) != len(testAnimations):
		return f"Animation count mismatch:\n\t{len(originalAnimations)} vs {len(testAnimations)}\n"
	
	if errStr != "":
		return errStr
	
	originalAnimationsDict = {}
	testAnimationsDict = {}

	for i in range(len(originalAnimations)):
		originalAnimation = originalAnimations[i]
		testAnimation = testAnimations[i]
		originalAnimationsDict[originalAnimation.get(C.ANIMATION_NAME, i)] = originalAnimation
		testAnimationsDict[testAnimation.get(C.ANIMATION_NAME, i)] = testAnimation

	animationNames = list(originalAnimationsDict.keys())
	testAnimationNames = list(testAnimationsDict.keys())
	animationNames.sort()

	errStr += CompareCommon.compare_array(len(animationNames), animationNames, testAnimationNames, C.__VAR_NAME, C.__VAR_NAME, C.GLTF_ANIMATION)

	if errStr != "":
		return errStr

	for animationName in animationNames:
		originalAnimation = originalAnimationsDict[animationName]
		testAnimation = testAnimationsDict[animationName]

		errStr += compare_animation(originalAnimation, testAnimation, originalBuffersCache, testBuffersCache, originalGltf, testGltf, f"{C.GLTF_ANIMATION}[{animationName}]", floatTolerance)

	return errStr

def compare_animation(originalAnimation, testAnimation, originalBuffersCache, testBuffersCache, originalGltf, testGltf, ownerHint, floatTolerance) -> str:
	errStr = ""

	errStr += compare_samplers_array(originalAnimation, testAnimation, ownerHint)
	if errStr != "":
		return errStr
	errStr += CompareCommon.compare_name(originalAnimation, testAnimation, C.GLTF_ANIMATION, ownerHint)
	compare_channels(originalAnimation, testAnimation, originalBuffersCache, testBuffersCache, originalGltf, testGltf, ownerHint, floatTolerance)

	return errStr

def compare_channels(originalAnimation, testAnimation, originalBuffersCache, testBuffersCache, originalGltf, testGltf, ownerHint, floatTolerance) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.ANIMATION_CHANNELS, originalAnimation, testAnimation, ownerHint, C.GLTF_ANIMATION)
	if errStr != "":
		return errStr
	
	originalChannels = originalAnimation[C.ANIMATION_CHANNELS]
	testChannels = testAnimation[C.ANIMATION_CHANNELS]

	originalSamplers = originalAnimation[C.ANIMATION_SAMPLERS]
	testSamplers = testAnimation[C.ANIMATION_SAMPLERS]

	originalAccessors = CompareAccessor.get_accessors(originalGltf)
	testAccessors = CompareAccessor.get_accessors(testGltf)

	if len(originalChannels) != len(testChannels):
		errStr += f"Animation[{ownerHint}] has mismatched samplers size:\n\t({len(originalChannels)} - {originalChannels}\n\t({len(testChannels)}) - {testChannels})\n"

	if errStr != "":
		return errStr

	originalChannelMap = {}
	testChannelMap = {}

	for i in range(len(originalChannels)):
		originalChannelTarget = originalChannels[i].get(C.ANIMATION_CHANNEL_TARGET, None)
		testChannelTarget = testChannels[i].get(C.ANIMATION_CHANNEL_TARGET, None)
		
		if originalChannelTarget == None:
			errStr += f"Original:{ownerHint}.channels[{i}] does not have a target specified.\n"
		if testChannelTarget == None:
			errStr += f"Test:{ownerHint}.channels[{i}] does not have a target specified.\n"

		if errStr != "":
			continue

		originalChannelTarget = originalChannelTarget.get(C.ANIMATION_CHANNEL_TARGET_PATH, None)
		testChannelTarget = testChannelTarget.get(C.ANIMATION_CHANNEL_TARGET_PATH, None)

		if originalChannelTarget == None:
			errStr += f"Original:{ownerHint}.channels[{i}] does not have a target specified.\n"
		if testChannelTarget == None:
			errStr += f"Test:{ownerHint}.channels[{i}] does not have a target specified.\n"

		if errStr != "":
			continue
		
		originalChannelMap[originalChannelTarget] = originalChannels[i]
		testChannelMap[testChannelTarget] = testChannels[i]

	originalChannelsKeysSorted = list(originalChannelMap.keys())
	testChannelsKeysSorted = list(testChannelMap.keys())
	originalChannelsKeysSorted.sort()
	testChannelsKeysSorted.sort()

	errStr += CompareCommon.compare_array(len(originalChannelsKeysSorted), originalChannelsKeysSorted, testChannelsKeysSorted, ownerHint, C.ANIMATION_CHANNEL_TARGET, C.GLTF_ANIMATION)

	if errStr != "":
		return errStr

	for channelTarget in originalChannelsKeysSorted:
		originalChannel = originalChannelMap[channelTarget]
		testChannel = testChannelMap[channelTarget]

		originalSamplerID = originalChannel.get(C.ANIMATION_CHANNEL_SAMPLER, -1)
		testSamplerID = testChannel.get(C.ANIMATION_CHANNEL_SAMPLER, -1)
		testSampler = None
		originalSampler = None

		if originalSamplerID < len(originalSamplers):
			originalSampler = originalSamplers[originalSamplerID]
		else:
			errStr += f"Original:[{ownerHint}].{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER} is out of bounds: ({originalSamplerID}/{len(originalSamplers)})\n"
		if testSamplerID < len(testSamplers):
			testSampler = testSamplers[testSamplerID]
		else:
			errStr += f"Test:[{ownerHint}].{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER} is out of bounds: ({testSamplerID}/{len(testSamplers)})\n"

		if errStr != "":
			continue

		originalSamplerInterpolation = originalSampler.get(C.ANIMATION_SAMPLER_INTERPOLATION, C.ANIMATION_SAMPLER_INTERPOLATION_TYPE_LINEAR)
		testSamplerInterpolation = testSampler.get(C.ANIMATION_SAMPLER_INTERPOLATION, C.ANIMATION_SAMPLER_INTERPOLATION_TYPE_LINEAR)

		if originalSamplerInterpolation != testSamplerInterpolation:
			errStr += f"Mismatch between {ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}]:\n\t{originalSamplerInterpolation}\n\t{testSamplerInterpolation}"

		originalSamplerInputAccessorID = originalSampler.get(C.ANIMATION_SAMPLER_INPUT, -1)
		testSamplerInputAccessorID = testSampler.get(C.ANIMATION_SAMPLER_INPUT, -1)
		originalSamplerOutputAccessorID = originalSampler.get(C.ANIMATION_SAMPLER_OUTPUT, -1)
		testSamplerOutputAccessorID = testSampler.get(C.ANIMATION_SAMPLER_OUTPUT, -1)

		originalInputAccessor = None
		testInputAccessor = None
		originalOutputAccessor = None
		testOutputAccessor = None


		if originalSamplerInputAccessorID < len(originalAccessors):
			originalInputAccessor = originalAccessors[originalSamplerInputAccessorID]
		else:
			errStr += f"Original:{ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}].{C.ANIMATION_SAMPLER_INPUT} is out of bounds: ({originalSamplerInputAccessorID}/{len(originalAccessors)})\n"
		if testSamplerInputAccessorID < len(testAccessors):
			testInputAccessor = testAccessors[testSamplerInputAccessorID]
		else:
			errStr += f"Test:{ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}].{C.ANIMATION_SAMPLER_INPUT} is out of bounds: ({testSamplerInputAccessorID}/{len(testAccessors)})\n"

		if originalSamplerOutputAccessorID < len(originalAccessors):
			originalOutputAccessor = originalAccessors[originalSamplerOutputAccessorID]
		else:
			errStr += f"Original:{ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}].{C.ANIMATION_SAMPLER_OUTPUT} is out of bounds: ({originalSamplerOutputAccessorID}/{len(originalAccessors)})\n"
		if testSamplerOutputAccessorID < len(testAccessors):
			testOutputAccessor = testAccessors[testSamplerOutputAccessorID]
		else:
			errStr += f"Test:{ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}].{C.ANIMATION_SAMPLER_OUTPUT} is out of bounds: ({testSamplerOutputAccessorID}/{len(testAccessors)})\n"

		if errStr != "":
			continue

		errStr += CompareAccessor.compare_accessor(originalInputAccessor, testInputAccessor, originalBuffersCache, testBuffersCache, floatTolerance, originalGltf, testGltf, f"{ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}].{C.ANIMATION_SAMPLER_INPUT}")
		errStr += CompareAccessor.compare_accessor(originalOutputAccessor, testOutputAccessor, originalBuffersCache, testBuffersCache, floatTolerance, originalGltf, testGltf, f"{ownerHint}.{C.ANIMATION_CHANNELS}.{C.ANIMATION_CHANNEL_SAMPLER}[{channelTarget}].{C.ANIMATION_SAMPLER_OUTPUT}")



	return errStr

# do not compare the contents, only check if the size matches
def compare_samplers_array(originalAnimation, testAnimation, ownerHint) -> str:
	errStr = ""

	errStr += CompareCommon.check_required_key(C.ANIMATION_SAMPLERS, originalAnimation, testAnimation, ownerHint, C.GLTF_ANIMATION)
	if errStr != "":
		return errStr
	
	originalSamplers = originalAnimation[C.ANIMATION_SAMPLERS]
	testSamplers = testAnimation[C.ANIMATION_SAMPLERS]

	if len(originalSamplers) != len(testSamplers):
		errStr += f"Animation[{ownerHint}] has mismatched samplers size:\n\t({len(originalSamplers)} - {originalSamplers}\n\t({len(testSamplers)}) - {testSamplers})\n"

	return errStr