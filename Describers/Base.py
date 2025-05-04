from io_ggltf import Constants as C
from io_ggltf.Core.Util import try_get_object, try_get_bone

class Describer:

	def __init__(self):
		self._name: str = None
		self._isExported: bool = False
		self._isReserved: bool = False
		self._reservedID: int = None
		self._exportedData: dict = {}
		self._dataTypeHint: str = None

	def _export(self, isBinary: bool, gltfDict: dict, fileTargetPath: str) -> bool:
		print(f"Describer: {self} has not overriden internal method '_export'.")
		return False
	
	def _export_name(self):
		if self._name != "" and self._name != None:
			self._exportedData[C.NODE_NAME] = self._name

	def _get_id_reservation(self, gltfDict: dict) -> int:
		if self._isReserved:
			return self._reservedID
		
		array = gltfDict[self._dataTypeHint]
		self._reservedID = len(array)
		self._isReserved = True
		array.append(None)
		return self._reservedID

	def _get_exported_dict(self) -> dict:
		return self._exportedData
	
	def set_name(self, name: str):
		if self._isExported:
			print(f"Attempted to change name of resolved describer: {self}.")
		else:
			self._name = name
	
	def get_name(self) -> str:
		return self._name
	
	def get_referenced_describers(self) -> set:
		return set()
	
class ObjectBasedDescriber(Describer):
	def __init__(self):
		super().__init__()

		self._objectName: str = None
		self._objectLibrary: str = None
		self._boneName: str = None
		self._hasValidObject = False

	def set_target(self, objName: str, objLibrary: str = None, boneName: str = None) -> bool:
		if not self._isExported:
			target = None
			if boneName != None:
				target = try_get_bone((objName, objLibrary, boneName))
			else:
				target = try_get_object((objName, objLibrary))

			if target == None:
				self._objectName = None
				self._objectLibrary = None
				self._boneName = None
				self._hasValidObject = False
				return False
			else:
				self._name = objName
				self._objectName = objName
				self._objectLibrary = objLibrary
				self._boneName = boneName
				self._hasValidObject = True
				return True
		else:
			print(f"Attempted to set object or bone on {self} after it is already exported.")