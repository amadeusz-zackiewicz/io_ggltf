from io_ggltf import Constants as C
from io_ggltf.Extensions import ExtensionObserver
from io_ggltf.Describers.Accessor import AccessorDescriber
from io_ggltf.Describers.Buffer import BufferDescriber

# https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_animation_pointer

class KHRAnimationPointers(ExtensionObserver):
	def __init__(self, file, target, **kwargs):
		super().__init__("KHR_animation_pointer", file, target, kwargs=kwargs)

		self._POINTER_KEY = "pointer"

	def notify(self, notificationHint, **kwargs):
		if notificationHint == C.EXTENSION_NOTIFICATION_ANIM_FILL_EXPORT:
			
			exportChannels: list = kwargs["exportChannels"]
			exportSamplers: list = kwargs["exportSamplers"]
			steppedInterpolation: bool = kwargs["steppedInterpolation"]
			isBinary: bool = kwargs["isBinary"]
			gltfDict: dict = kwargs["gltfDict"]
			fileTargetPath: str = kwargs["fileTargetPath"]
			buffer: BufferDescriber = kwargs["buffer"]
			extensionSamplers: list = kwargs["extensionSamplers"]

			for extensionSampler in extensionSamplers:
				observer = extensionSampler._observer

				input = AccessorDescriber()
				inputMax = [extensionSampler.keys[-1]]
				inputMin = [extensionSampler.keys[0]]
				input.insert_data(extensionSampler.keys,
					buffer,
					C.ACCESSOR_TYPE_SCALAR,
					C.ACCESSOR_COMPONENT_TYPE_FLOAT,
					C.PACKING_FORMAT_FLOAT,
					inputMax,
					inputMin)
				
				output = AccessorDescriber()
				output.insert_data(extensionSampler.values,
					buffer,
					observer.animation_type(),
					observer.animation_component_type(),
					observer.animation_packing_format()
					)
				
				input._export(isBinary, gltfDict, fileTargetPath)
				output._export(isBinary, gltfDict, fileTargetPath)

				samplerInterpolation: str = \
					C.ANIMATION_SAMPLER_INTERPOLATION_TYPE_STEP \
						  if observer.animation_is_force_stepped() or steppedInterpolation \
							  else C.ANIMATION_SAMPLER_INTERPOLATION_TYPE_LINEAR

				sampler = {
					C.ANIMATION_SAMPLER_INTERPOLATION: samplerInterpolation,
					C.ANIMATION_SAMPLER_INPUT: input._get_id_reservation(gltfDict),
					C.ANIMATION_SAMPLER_OUTPUT: output._get_id_reservation(gltfDict)
				}

				samplerID = len(exportSamplers)
				exportSamplers.append(sampler)

				channel = {
					C.ANIMATION_CHANNEL_SAMPLER: samplerID,
					C.ANIMATION_CHANNEL_TARGET: {
						C.ANIMATION_CHANNEL_TARGET_PATH: C.ANIMATION_CHANNEL_TARGET_TYPE_POINTER,
						C.ANIMATION_CHANNEL_TARGET_EXTENSION: {
							self._extensionID: {
								self._POINTER_KEY: observer.get_animation_path(gltfDict)}
						}
					}
				}

				gltfDict[C.GLTF_ACCESSOR][input._get_id_reservation(gltfDict)] = input._exportedData
				gltfDict[C.GLTF_ACCESSOR][output._get_id_reservation(gltfDict)] = output._exportedData
				gltfDict[C.GLTF_BUFFER_VIEW][input._bufferView._get_id_reservation(gltfDict)] = input._bufferView._exportedData
				gltfDict[C.GLTF_BUFFER_VIEW][output._bufferView._get_id_reservation(gltfDict)] = output._bufferView._exportedData
				exportChannels.append(channel)
				
