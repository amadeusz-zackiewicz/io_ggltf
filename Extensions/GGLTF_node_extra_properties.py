from io_ggltf import Constants as C
from io_ggltf.Core import Util
from .ExtensionObserver import ExtensionObserver

class NodeExtraProperty(ExtensionObserver):
	def __init__(self, file, target, blenderProperty: str, exportProperty: str = None, includeTypeInfo: bool = True, animate: bool = True, **kwargs):
		super().__init__("ggltf_extra_properties", file, target, kwargs)
		self._blenderProperty = blenderProperty
		self._exportProperty = exportProperty if exportProperty != None else blenderProperty
		self._includeTypeInfo = includeTypeInfo

		self._TYPE_DATA_DICT_KEY = "types"
		self._VALUE_DICT_KEY = "values"

		self._enable_animation = animate
		self._fallback = None

	def set_fallback_value(self, value):
		self._fallback = value

	def notify(self, notificationHint, **kwargs):
		if notificationHint == C.NODE_NOTIFICATION_POST_CORE_EXPORT:
			value = self.get_value_at_current_frame()

			if self._includeTypeInfo:
				self._insert_type_info(
					{
						C.ACCESSOR_TYPE: self.get_type(),
						C.ACCESSOR_COMPONENT_TYPE: self.get_component_type()}
					)
			self._insert_value(value)


	def _insert_type_info(self, dataDict: dict):
		exportData = self._get_own_dict_from_target()
		typeDict = exportData.get(self._TYPE_DATA_DICT_KEY)

		if typeDict == None:
			typeDict = {}
			exportData[self._TYPE_DATA_DICT_KEY] = typeDict

		typeDict[self._exportProperty] = dataDict

	def _insert_value(self, value):
		exportData = self._get_own_dict_from_target()
		valueDict = exportData.get(self._VALUE_DICT_KEY)

		if valueDict == None:
			valueDict = {}
			exportData[self._VALUE_DICT_KEY]
		
		valueDict[self._exportProperty] = value

	def get_value_at_current_frame(self):
		if self._target._hasValidObject == False:
			return self._fallback
		obj = Util.try_get_object(self._target.get_target())

		if obj == None:
			return self._fallback
		
		return obj.get(self._blenderProperty)


	def get_export_property_name(self) -> str:
		return self._exportProperty
	
	def get_animation_path(self, gltfDict: dict) -> str:
		return f"/nodes/{self._target._get_id_reservation(gltfDict)}/{self._extensionID}/{self._VALUE_DICT_KEY}/{self.get_export_property_name}"

class NodeBoolean(NodeExtraProperty):
	def __init__(self, file, target, blenderProperty: str, exportProperty: str = None, includeTypeInfo: bool = True, animate: bool = True):
		super().__init__(file, target, blenderProperty, exportProperty, False, animate)

	def get_value_at_current_frame(self):
		value = super().get_value_at_current_frame()

		if value != None:
			return value
		else:
			return None

	def animation_is_allowed(self) -> bool:
		return True

	def animation_component_type(self) -> int:
		return C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_BYTE
	
	def animation_type(self) -> str:
		return C.ACCESSOR_TYPE_SCALAR
	
	def animation_packing_format(self):
		return C.PACKING_FORMAT_U_INT
	
	def animation_is_force_stepped(self) -> bool:
		return True

			