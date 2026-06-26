from io_ggltf import Constants as C
from io_ggltf.Extensions import ExtensionObserver
from io_ggltf.Core import Util, BlenderUtil

# https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_node_visibility
class KHRNodeVisibility(ExtensionObserver):
	def __init__(self, file, target, animate: bool = True, **kwargs):
		super().__init__("KHR_node_visibility", file, target, kwargs=kwargs)

		self._VALUE_DICT_KEY = "value"

		self._enableAnimation = animate
		self._fallback: bool = True

	def set_fallback_value(self, value: bool):
		self._fallback = value

	def notify(self, notificationHint, **kwargs):
		if notificationHint == C.EXTENSION_NOTIFICATION_NODE_POST_EXPORT:
			exportData = self._get_own_dict_from_target()
			exportData[self._VALUE_DICT_KEY] = self.get_value_at_current_frame()

	def animation_component_type(self):
		return C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_BYTE
	
	def animation_type(self):
		return C.ACCESSOR_TYPE_SCALAR
	
	def animation_packing_format(self):
		return C.PACKING_FORMAT_U_INT
	
	def animation_is_allowed(self) -> bool:
		return True

	def animation_is_force_stepped(self):
		return True
	
	def get_animation_path(self, gltfDict: dict) -> str:
		return f"/nodes/{self._target._get_id_reservation(gltfDict)}/{self._extensionID}/{self._VALUE_DICT_KEY}"

	def get_value_at_current_frame(self):
		if self._target._hasValidObject == False:
			return self._fallback
		obj = Util.try_get_object(self._target.get_target())

		if obj == None:
			return self._fallback

		return obj.get("hide_viewport", self._fallback)

