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
		#self._sampleSkins: set[SkinDescriber] = set()
		self._boneFilter: tuple[str, bool] = None
		self._objectFilter: tuple[str, bool] = None
		self._steppedInterpolation = False
		self._optimise = True

		self._returnFrame: float = 1.0 # frame to return to when export is done


	def add_NLA_track(self, nlaTrackName: str, trackOwnerName: str = None, trackOwnerLibrary: str = None):
		if not self._isExported:
			self._nlaTracks.append(nlaTrackName)
			self._nlaTracksOwnerName.append(trackOwnerName)
			self._nlaTracksOwnerLibraries.append(trackOwnerLibrary)
		else:
			print(f"Tried to add nla tracks to already exported animation")
		return self

	def add_animation_targets(self, describers: Describer | list[Describer] | tuple[Describer] | set[Describer]):
		if not self._isExported:
			if type(describers) == list or type(describers) == tuple or type(describers) == set:
				for desc in describers:
					self.__try_add_describer_to_targets(desc)
			else:
				self.__try_add_describer_to_targets(describers)
		else:
			print(f"Tried to add animation targets to already exported animation")
		return self

	def set_use_step_interpolation(self, useSteppedInterpolation: bool):
		if not self._isExported:
			self._steppedInterpolation = useSteppedInterpolation
		else:
			print(f"Tried to change interpolation on already exported animation")
		return self
		
	def get_use_step_interpolation(self):
		return self._steppedInterpolation

	def set_optimise(self, optimise: bool):
		if not self._isExported:
			self._optimise = optimise
		else:
			print(f"Tried to change optimisation on already exported animation")
		return self
		
	def get_is_optimised(self):
		return self._optimise
		
	def _export_name(self):
		super()._export_name()

		if not C.ANIMATION_NAME in self._exportedData:
			if len(self._nlaTracks) > 0:
				self._exportedData[C.ANIMATION_NAME] = self._nlaTracks[0]
		
	def __try_add_describer_to_targets(self, describer: Describer):
		if describer._dataTypeHint == C.GLTF_NODE:
			self._sampleNodes.add(describer)

	def __flatten_describers(self):
		describers = set()
		for sampleNode in self._sampleNodes:
			hierarchy = sampleNode.get_flattened_hierarchy()
			for offspring in hierarchy:
				describers.add(offspring)

		return describers

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

	def __export_trs(self, isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels, targetChannel):
		if targetChannel == None or len(targetChannel.keys) == 0:
			return

		input = self.__create_input_accessor(targetChannel.keys)
		output = AccessorDescriber()
		channelTypeHint: str

		if targetChannel.transformSampleOffset == 1:
			channelTypeHint = C.NODE_ROTATION
			output.insert_data(targetChannel.values,
				self._buffer, C.ACCESSOR_TYPE_VECTOR_4, C.ACCESSOR_COMPONENT_TYPE_FLOAT, C.PACKING_FORMAT_FLOAT)
		else:
			if targetChannel.transformSampleOffset == 0:
				channelTypeHint = C.NODE_TRANSLATION
			else:
				channelTypeHint = C.NODE_SCALE

			output.insert_data(targetChannel.values,
				self._buffer, C.ACCESSOR_TYPE_VECTOR_3, C.ACCESSOR_COMPONENT_TYPE_FLOAT, C.PACKING_FORMAT_FLOAT)
			
		self.__export_input_output_accessors(input, output, isBinary, gltfDict, fileTargetPath)

		exportChannels.append(self.__create_channel(len(exportSamplers), nodeSampler.nodeDescriber._get_id_reservation(gltfDict), channelTypeHint))
		exportSamplers.append(self.__create_sampler(input._get_id_reservation(gltfDict), output._get_id_reservation(gltfDict)))


	def __export_translation(self, isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels):
		self.__export_trs(isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels, nodeSampler.translationChannel)

	def __export_rotation(self, isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels):
		self.__export_trs(isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels, nodeSampler.rotationChannel)

	def __export_scale(self, isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels):
		self.__export_trs(isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels, nodeSampler.scaleChannel)

	def __export_weights(self, isBinary, gltfDict, fileTargetPath, nodeSampler, exportSamplers, exportChannels):
		channel: WeightsChannel = nodeSampler.weightsChannel
		if channel == None or (channel.keys) == 0:
			return
		
		input = self.__create_input_accessor(channel.keys)
		output = AccessorDescriber()
		flattened_values = []
		for weights in channel.values:
			for weight in weights:
				flattened_values.append(weight)

		output.insert_data(flattened_values, self._buffer, C.ACCESSOR_TYPE_SCALAR, C.ACCESSOR_COMPONENT_TYPE_FLOAT, C.PACKING_FORMAT_FLOAT)

		self.__export_input_output_accessors(input, output, isBinary, gltfDict, fileTargetPath)
		
		exportChannels.append(self.__create_channel(len(exportSamplers), nodeSampler.nodeDescriber._get_id_reservation(gltfDict), C.NODE_WEIGHTS))
		exportSamplers.append(self.__create_sampler(input._get_id_reservation(gltfDict), output._get_id_reservation(gltfDict)))

		
	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			if self.__is_frame_step_invalid():
				print(f"Frame step of {self._frameStep} is not valid.")
				self._isExported = True
				return False

			sceneArmatures, armatureStates = BlenderUtil.snapshot_all_armature_obj_states()
			BlenderUtil.set_all_armatures_to_pose_mode(C.BLENDER_ARMATURE_POSE_MODE)
			nodesToAnimate = self.__flatten_describers()
			# TODO: if even a single node has custom property to animate then add extension info

			nodeSamplers: list[NodeSampler] = [NodeSampler] * len(nodesToAnimate)

			for iNode, node in enumerate(nodesToAnimate):
				sampler = NodeSampler(node)

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
					Timeline.set_frame(currentFrame, depsGraph)

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
				if nodeSampler.animateTRS:
					self.__export_translation(isBinary, gltfDict, fileTargetPath, nodeSampler, exportedSamplers, exportedChannels)
					self.__export_rotation(isBinary, gltfDict, fileTargetPath, nodeSampler, exportedSamplers, exportedChannels)
					self.__export_scale(isBinary, gltfDict, fileTargetPath, nodeSampler, exportedSamplers, exportedChannels)

				if nodeSampler.weightsChannel != None:
					self.__export_weights(isBinary, gltfDict, fileTargetPath, nodeSampler, exportedSamplers, exportedChannels)

			
			self._exportedData[C.ANIMATION_CHANNELS] = exportedChannels
			self._exportedData[C.ANIMATION_SAMPLERS] = exportedSamplers

			if len(extensionChannels) > 0:
				pass

			self.__revert_track_states(originalTrackStates)
			BlenderUtil.reset_all_armature_obj_states(sceneArmatures, armatureStates)
			Timeline.set_frame(beforeFrame, depsGraph)
			self._isExported = True
			
			return True
		else:
			print(f"Tried to export animation that is already exported.")

class NodeSampler:
	def __init__(self, nodeDescriber: NodeDescriber):
		self.nodeDescriber: NodeDescriber = nodeDescriber

		self.translationChannel: TranslationChannel = None
		self.rotationChannel: RotationChannel = None
		self.scaleChannel: ScaleChannel = None
		self.weightsChannel: WeightsChannel = None
		
		self.animateTRS: bool = False

		animateTransform = nodeDescriber.get_animate_transforms()

		if animateTransform[0] == True:
			self.translationChannel = TranslationChannel(nodeDescriber)
			self.animateTRS = True
		if animateTransform[1] == True:
			self.rotationChannel = RotationChannel(nodeDescriber)
			self.animateTRS = True
		if animateTransform[2] == True:
			self.scaleChannel = ScaleChannel(nodeDescriber)
			self.animateTRS = True

		if nodeDescriber.get_animate_mesh_weights() and nodeDescriber._mesh != None:
			self.weightsChannel = WeightsChannel(nodeDescriber)

		self.extraChannels: list[ExtensionChannel] = []

	def sample(self, time: float):
		transform = None

		if self.animateTRS:
			parent = self.nodeDescriber.get_parent()
			if parent != None:
				transform = Util.get_yup_transforms(self.nodeDescriber.get_target(), parent.get_target())
			else:
				transform = Util.get_yup_transforms(self.nodeDescriber.get_target(), None)

		if self.translationChannel != None:
			self.translationChannel.sample_trs(time, transform)
		if self.rotationChannel != None:
			self.rotationChannel.sample_trs(time, transform)
		if self.scaleChannel != None:
			self.scaleChannel.sample_trs(time, transform)

		if self.weightsChannel != None:
			self.weightsChannel.sample_weights(time)

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
			print
			for popID in popIDs:
				_ = keys.pop(popID)
				_ = values.pop(popID)

	def optimise(self):
		if self.translationChannel != None:
			self.optimise_channel(self.translationChannel.keys, self.translationChannel.values)
		if self.rotationChannel != None:
			self.optimise_channel(self.rotationChannel.keys, self.rotationChannel.values)
		if self.scaleChannel != None:
			self.optimise_channel(self.scaleChannel.keys, self.scaleChannel.values)
		if self.weightsChannel != None:
			self.optimise_channel(self.weightsChannel.keys, self.weightsChannel.values)
		
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
		self.keys: list[float] = []
		self.values: list[list[float]] = []
		self.transformSampleOffset: int = 0

	def sample_trs(self, time: float, precalculated_transform):
		self.keys.append(time)
		self.values.append(Util.bl_math_to_gltf_list(precalculated_transform[self.transformSampleOffset]))

class TranslationChannel(TRSChannel):
	def __init__(self, node: NodeDescriber):
		super().__init__(node)
		self.transformSampleOffset = 0

class RotationChannel(TRSChannel):
	def __init__(self, node: NodeDescriber):
		super().__init__(node)
		self.transformSampleOffset = 1

class ScaleChannel(TRSChannel):
	def __init__(self, node: NodeDescriber):
		super().__init__(node)
		self.transformSampleOffset = 2

class WeightsChannel(ChannelBase):
	def __init__(self, node: NodeDescriber):
		super().__init__(node)

		self.keys: list[float] = []
		self.values: list[list[float]] = []

	def sample_weights(self, time: float):
		weights = self.node.get_weights_from_mesh()
		self.keys.append(time)
		self.values.append(weights)


class ExtensionChannel(ChannelBase):
	def __init__(self, node: NodeDescriber, propertyName: str):
		super().__init__(node)

		self.propertyName: str = propertyName
		self.keys: list[float] = [] # time
		self.values: list = []

	def sample_property(self, time: float):
		pass


