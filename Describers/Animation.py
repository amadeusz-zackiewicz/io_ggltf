from io_ggltf import Constants as C
from io_ggltf.Core import Util, BlenderUtil
from io_ggltf.Describers import *

from io_ggltf.Core.Blender import NLA, Timeline

class AnimationDescriber(Describer):
	def __init__(self, buffer: BufferDescriber):
		super().__init__()

		self._dataTypeHint = C.GLTF_ANIMATION

		self._buffer = buffer
		self._frameStep = 1.0
		self._frameStart = None
		self._frameEnd = None
		self._nlaTracksOwnerName: list[str] = []
		self._nlaTracksOwnerLibraries: list[str] = []
		self._nlaTracks: list[str] = []
		self._sampleNodes: set[NodeDescriber] = set()
		self._sampleSkins: set[SkinDescriber] = set()
		self._boneFilter: tuple[str, bool] = None
		self._objectFilter: tuple[str, bool] = None
		self._steppedInterpolation = False
		self._optimise = True

		self._returnFrame: float = 1.0 # frame to return to when export is done


	def add_NLA_track(self, nlaTrackName: str, trackOwnerName: str = None, trackOwnerLibrary:str = None):
		if not self._isExported:
			self._nlaTracks.append(nlaTrackName)
			self._nlaTracksOwnerName.append(trackOwnerName)
			self._nlaTracksOwnerLibraries.append(trackOwnerLibrary)
		else:
			return print(f"Tried to add nla tracks to already exported animation")

	def add_animation_targets(self, describers: Describer | list[Describer] | tuple[Describer] | set[Describer]):
		if not self._isExported:
			if type(describers) == list or type(describers) == tuple or type(describers) == set:
				for desc in describers:
					self.__try_add_describer_to_targets(desc)
			else:
				self.__try_add_describer_to_targets(describers)
		else:
			return print(f"Tried to add animation targets to already exported animation")

	def set_use_step_interpolation(self, useSteppedInterpolation: bool):
		if not self._isExported:
			self._steppedInterpolation = useSteppedInterpolation
		else:
			return print(f"Tried to change interpolation on already exported animation")

	def set_optimise(self, optimise: bool):
		if not self._isExported:
			self._optimise = optimise
		else:
			return print(f"Tried to change optimisation on already exported animation")
		
	def _export_name(self):
		super()._export_name()

		if not C.ANIMATION_NAME in self._exportedData:
			if len(self._nlaTracks) > 0:
				self._exportedData[C.ANIMATION_NAME] = self._nlaTracks[0]
		
	def __try_add_describer_to_targets(self, describer: Describer):
		if describer._dataTypeHint == C.GLTF_NODE:
			self._sampleNodes.add(describer)
		elif describer._dataTypeHint == C.GLTF_SKIN:
			self._sampleNodes.add(describer)

	def __flatten_describers(self):
		def add_child_nodes_recursive(node: NodeDescriber):
			for child in node._children:
				add_child_nodes_recursive(child)
				describers.append(child)
				describers.append([])
		
		describers: list[NodeDescriber] = []
		extraProps: list[str] = []

		for skin in self._sampleSkins:
			jointNodes = skin._boneNodeDescribers

			if self._boneFilter != None:
				for joint in jointNodes:
					if Util.name_passes_filter(self._boneFilter, joint._boneName):
						describers.append(joint)
						extraProps.append([])
			else:
				for joint in jointNodes:
					describers.append(joint)
					extraProps.append([])

		if self._objectFilter != None:
			for node in self._sampleNodes:
				if Util.name_passes_filter(self._objectFilter, node._objectName):
					describers.append(node)
					extraProps.append([])
		else:
			for node in self._sampleNodes:
				describers.append(node)
				extraProps.append([])
			
		if self._objectFilter != None:
			for i in range(len(describers), -1, -1):
				if not Util.name_passes_filter(self._objectFilter, describers[i]._objectName):
					_ = describers.pop(i)

		return describers, extraProps

	def __snapshot_all_tracks_states(self):
		return NLA.get_snapshot_of_all_nla_tracks_states()
	
	def __revert_track_states(self, states):
		NLA.set_all_nla_tracks_from_snapshot(states)

	def __is_frame_step_invalid(self):
		if self._frameStep == 0.0:
			return False

	def __calculate_frame_range(self):
		autoStartFrame, autoEndFrame = NLA.get_nla_tracks_framerange(self._nlaTracksOwnerName, self._nlaTracksOwnerLibraries, self._nlaTracks)

		if self._frameStart == None:
			self._frameStart = autoStartFrame
		if self._frameEnd == None:
			self._frameEnd = autoEndFrame

	def __is_reverse(self):
		if self._frameStep < 0.0:
			return True
		else:
			return False
		
	def __export_input_output_accessors(self, input: AccessorDescriber, output: AccessorDescriber, isBinary: bool, gltfDict: dict, fileTargetPath: str):
		input._export(isBinary, gltfDict, fileTargetPath)
		output._export(isBinary, gltfDict, fileTargetPath)
		gltfDict[C.GLTF_ACCESSOR][input._get_id_reservation(gltfDict)] = input._exportedData
		gltfDict[C.GLTF_ACCESSOR][output._get_id_reservation(gltfDict)] = output._exportedData
		gltfDict[C.GLTF_BUFFER_VIEW][input._bufferView._get_id_reservation(gltfDict)] = input._bufferView._exportedData
		gltfDict[C.GLTF_BUFFER_VIEW][output._bufferView._get_id_reservation(gltfDict)] = output._bufferView._exportedData

	def __create_input_accessor(self, data):
		input = AccessorDescriber()
		input.insert_data(data,
				self._buffer,
				C.ACCESSOR_TYPE_SCALAR,
				C.ACCESSOR_COMPONENT_TYPE_FLOAT,
				C.PACKING_FORMAT_FLOAT, 
				[max(data)], 
				[min(data)])
		
		return input
	
	def __create_channel(self, samplerID: int, nodeID: int, targetProperty: str) -> dict:
		return {
			C.ANIMATION_CHANNEL_SAMPLER: samplerID,
			C.ANIMATION_CHANNEL_TARGET: {
				C.ANIMATION_CHANNEL_TARGET_NODE: nodeID,
				C.ANIMATION_CHANNEL_TARGET_PATH: targetProperty
			}
		}
	
	def __create_sampler(self, inputID: int, outputID: int) -> dict:
		sampler =  {
			C.ANIMATION_SAMPLER_INPUT: inputID,
			C.ANIMATION_SAMPLER_OUTPUT: outputID
		}

		if self._steppedInterpolation:
			sampler[C.ANIMATION_SAMPLER_INTERPOLATION] = C.ANIMATION_SAMPLER_INTERPOLATION_TYPE_STEP

		return sampler

	def __export_trs(self, isBinary, gltfDict, fileTargetPath, nodeSampler, allSamplers, allChannels):
		if len(nodeSampler.trs.translationKeys) > 0:
			input = self.__create_input_accessor(nodeSampler.trs.translationKeys)
			output = AccessorDescriber()
			output.insert_data(nodeSampler.trs.translationValues,
				self._buffer, C.ACCESSOR_TYPE_VECTOR_3, C.ACCESSOR_COMPONENT_TYPE_FLOAT, C.PACKING_FORMAT_FLOAT)
			self.__export_input_output_accessors(input, output, isBinary, gltfDict, fileTargetPath)
			
			allChannels.append(self.__create_channel(len(allSamplers), nodeSampler.nodeDescriber._get_id_reservation(gltfDict), C.NODE_TRANSLATION))
			allSamplers.append(self.__create_sampler(input._get_id_reservation(gltfDict), output._get_id_reservation(gltfDict)))

		if len(nodeSampler.trs.rotationKeys) > 0:
			input = self.__create_input_accessor(nodeSampler.trs.rotationKeys)
			output = AccessorDescriber()
			output.insert_data(nodeSampler.trs.rotationValues,
				self._buffer, C.ACCESSOR_TYPE_VECTOR_4, C.ACCESSOR_COMPONENT_TYPE_FLOAT, C.PACKING_FORMAT_FLOAT)
			self.__export_input_output_accessors(input, output, isBinary, gltfDict, fileTargetPath)
			
			allChannels.append(self.__create_channel(len(allSamplers), nodeSampler.nodeDescriber._get_id_reservation(gltfDict), C.NODE_ROTATION))
			allSamplers.append(self.__create_sampler(input._get_id_reservation(gltfDict), output._get_id_reservation(gltfDict)))

		if len(nodeSampler.trs.scaleKeys) > 0:
			input = self.__create_input_accessor(nodeSampler.trs.scaleKeys)
			output = AccessorDescriber()
			output.insert_data(nodeSampler.trs.scaleValues,
				self._buffer, C.ACCESSOR_TYPE_VECTOR_3, C.ACCESSOR_COMPONENT_TYPE_FLOAT, C.PACKING_FORMAT_FLOAT)
			self.__export_input_output_accessors(input, output, isBinary, gltfDict, fileTargetPath)
			
			allChannels.append(self.__create_channel(len(allSamplers), nodeSampler.nodeDescriber._get_id_reservation(gltfDict), C.NODE_SCALE))
			allSamplers.append(self.__create_sampler(input._get_id_reservation(gltfDict), output._get_id_reservation(gltfDict)))

		
	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			if self.__is_frame_step_invalid():
				print(f"Frame step of {self._frameStep} is not valid.")
				self._isExported = True
				return False

			nodesToAnimate, extraProperties = self.__flatten_describers()

			for extraPropertiesNames in extraProperties:
				if len(extraPropertiesNames) > 0:
					if C.ANIMATION_EXTENSION in self._exportedData:
						self._exportedData[C.ANIMATION_EXTENSION][C.EXTENSION_BUILD_IN_EXTRA_PROPERTIES] = {}
					else:
						self._exportedData[C.ANIMATION_EXTENSION] = {C.EXTENSION_BUILD_IN_EXTRA_PROPERTIES: {}}
					break
			
			

			nodeSamplers: list[NodeSampler] = [NodeSampler] * len(nodesToAnimate)

			for iNode, node in enumerate(nodesToAnimate):
				sampler = NodeSampler(node, extraProperties[iNode])

				for extraPropsName in extraProperties[iNode]:
					sampler.extraChannels.append(ExtensionChannel(node, extraPropsName))

				nodeSamplers[iNode] = sampler

			self.__calculate_frame_range()

			beforeFrame: float = Timeline.get_current_frame()
			reverse: bool = self.__is_reverse()

			originalTrackStates = self.__snapshot_all_tracks_states()
			NLA.mute_all()
			for i, tracks in enumerate(self._nlaTracks):
				NLA.set_track_mute((self._nlaTracksOwnerName[i], self._nlaTracksOwnerLibraries[i]), tracks, False)

			depsGraph = BlenderUtil.get_depsgraph()

			if reverse:
				currentFrame: float = self._frameEnd
				while True:
					relativeFrameTime = Timeline.get_real_time(self._frameEnd - currentFrame)
					Timeline.set_frame(currentFrame, depsGraph)

					for nodeSampler in nodeSamplers:
						nodeSampler.sample(relativeFrameTime)

					currentFrame += self._frameStep

					if currentFrame < self._frameStart:
						break
			else:
				currentFrame: float = self._frameStart
				while True:
					relativeFrameTime = Timeline.get_real_time(currentFrame - self._frameStart)
					Timeline.set_frame(currentFrame)
					
					for nodeSampler in nodeSamplers:
						nodeSampler.sample(relativeFrameTime)

					currentFrame += self._frameStep

					if currentFrame > self._frameEnd:
						break

			if self._optimise:
				for nodeSampler in nodeSamplers:
					nodeSampler.optimise()

			self._export_name()

			exportedSamplers = []
			exportedChannels = []
			extensionSamplers = []
			extensionChannels = []

			for nodeSampler in nodeSamplers:
				if nodeSampler.trs != None:
					self.__export_trs(isBinary, gltfDict, fileTargetPath, nodeSampler, exportedSamplers, exportedChannels)

				if nodeSampler.weights != None:
					pass

				for extraChannel in nodeSampler.extraChannels:
					pass
			
			self._exportedData[C.ANIMATION_CHANNELS] = exportedChannels
			self._exportedData[C.ANIMATION_SAMPLERS] = exportedSamplers

			if len(extensionChannels) > 0:
				pass

			self.__revert_track_states(originalTrackStates)
			Timeline.set_frame(beforeFrame, depsGraph)
			self._isExported = True
			return True
		else:
			print(f"Tried to export animation that is already exported.")

class NodeSampler:
	def __init__(self, nodeDescriber: NodeDescriber, extraProperties: list[str]):
		self.nodeDescriber: NodeDescriber = nodeDescriber
		self.trs: TRSChannel = TRSChannel(nodeDescriber)
		self.weights: WeightsChannel = None
		if nodeDescriber._mesh != None:
			pass # TODO: add weights if shape keys are present
		self.extraChannels: list[ExtensionChannel] = [ExtensionChannel(nodeDescriber, prop) for prop in extraProperties]

	def sample(self, time: float):
		if self.trs != None:
			self.trs.sample_trs(time)
		if self.weights != None:
			self.weights.sample_weights(time)
		for channel in self.extraChannels:
			channel.sample_property(time)

	def optimise_channel(self, keys: list[float], values: list):
		if len(keys) > 2:
			popIDs = []
			i = len(values) - 2
			while i > 0:
				leftValue = values[i - 1]
				value = values[i]
				rightValue = values[i + 1]

				if leftValue == value and rightValue == value:
					popIDs.append(i)

				i -= 1

			for popID in popIDs:
				_ = keys.pop(popID)
				_ = values.pop(popID)

	def optimise(self):
		if self.trs != None:
			self.optimise_channel(self.trs.translationKeys, self.trs.translationValues)
			self.optimise_channel(self.trs.rotationKeys, self.trs.rotationValues)
			self.optimise_channel(self.trs.scaleKeys, self.trs.scaleValues)
		if self.weights != None:
			self.optimise_channel(self.weights.keys, self.weights.values)
		
		for extraChannel in self.extraChannels:
			self.optimise_channel(extraChannel.keys, extraChannel.values)

class ChannelBase:
	def __init__(self, node: NodeDescriber):
		self.node = node

		self._parentTuple: tuple = None
		self._selfTuple: tuple = None

		if self.node._parent != None:
			if self.node._parent._boneName != None:
				self._parentTuple = (self.node._parent._objectName, self.node._parent._objectLibrary, self.node._parent._boneName)
			else:
				self._parentTuple = (self.node._parent._objectName, self.node._parent._objectLibrary)

		if self.node._boneName != None:
			self._selfTuple = (self.node._objectName, self.node._objectLibrary, self.node._boneName)
		else:
			self._selfTuple = (self.node._objectName, self.node._objectLibrary)

class TRSChannel(ChannelBase):
	def __init__(self, node: NodeDescriber):
		super().__init__(node)

		self.translationKeys: list[float] = []
		self.rotationKeys: list[float] = []
		self.scaleKeys: list[float] = []

		self.translationValues: list[list[float]] = []
		self.rotationValues: list[list[float]] = []
		self.scaleValues: list[list[float]] = []

	def sample_trs(self, time: float):
		t, r ,s = Util.get_yup_transforms(self._selfTuple, self._parentTuple)

		t = Util.bl_math_to_gltf_list(t)
		r = Util.bl_math_to_gltf_list(r)
		s = Util.bl_math_to_gltf_list(s)

		self.translationKeys.append(time)
		self.rotationKeys.append(time)
		self.scaleKeys.append(time)

		self.translationValues.append(t)
		self.rotationValues.append(r)
		self.scaleValues.append(s)

class WeightsChannel(ChannelBase):
	def __init__(self, node: NodeDescriber):
		super().__init__(node)

		self.keys: list[float] = []
		self.values: list[list[float]] = []

	def sample_weights(self, time: float):
		pass

class ExtensionChannel(ChannelBase):
	def __init__(self, node: NodeDescriber, propertyName: str):
		super().__init__(node)

		self.propertyName: str = propertyName
		self.keys: list[float] = [] # time
		self.values: list = []

	def sample_property(self, time: float):
		pass


