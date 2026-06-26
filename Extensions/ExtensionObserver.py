from io_ggltf import Constants as C

class ExtensionObserver:
	def __init__(self, extensionID: str, file, target, **kwargs):
		self._extensionID = extensionID
		self._file = file
		self._target = target
		self._enableAnimation = False

		if not self in target._extensionObservers:
			target._extensionObservers.append(self)

		file.add_extension((self.get_extension_id(), self.is_extension_required()))

	def is_extension_required(self) -> bool:
		return False

	def get_extension_id(self) -> str:
		return self._extensionID

	def notify(self, notificationHint, **kwargs):
		return None

	def _get_own_dict_from_target(self) -> dict:
		extensionsDict = self._target._exportedData.get(C.GLTF_EXTENSION)
		if extensionsDict == None:
			extensionsDict = {}
			self._target._exportedData[C.GLTF_EXTENSION] = extensionsDict

		d = extensionsDict.get(self._extensionID)
		if d == None:
			d = {}
			extensionsDict[self._extensionID] = d

		return d
	
	def animation_is_allowed(self) -> bool:
		return False

	def set_animation_enabled(self, enabled: bool):
		self._enableAnimation = enabled

	def get_animation_enabled(self) -> bool:
		return self._enableAnimation

	def animation_allowed_and_enabled(self) -> bool:
		return self._enableAnimation and self.animation_is_allowed()
	
	def animation_component_type(self) -> int:
		return 0
	
	def animation_type(self) -> str:
		return ""
		
	def animation_packing_format(self) -> str:
		return None
	
	def animation_is_force_stepped(self) -> bool:
		return False
	
	def get_animation_path(self, gltfDict: dict) -> str:
		return None
	
	
	def get_value_at_current_frame(self):
		return None

	def animation_value_requires_flattening(self) -> bool:
		return False