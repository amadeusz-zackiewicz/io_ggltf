import Constants as C
from io_ggltf.Core.Util import try_get_object

class Describer:

	def __init__(self):
		self._name: str = None
		self._isResovled: bool = False
		self._isReserved: bool = False
		self._reservedID: int = None
		self._resolvedData: dict = {}
		self._dataTypeHint: str = None

	def _resolve(self, isBinary: bool, gltfDict: dict, fileTargetPath: str) -> bool:
		print(f"Describer: {self} has not overriden internal method '_resolve'.")
		return False

	def _get_id_reservation(self, gltfDict: dict) -> int:
		if self._isReserved:
			return self._reservedID
		
		array = gltfDict[self._dataTypeHint]
		self._reservedID = len(array)
		self._isReserved = True
		array.append(None)
		return self._reservedID

	def _get_resolved_dict(self) -> dict:
		return {}
	
class ObjectBasedDescriber(Describer):
	def __init__(self):
		super().__init__()

		self._objectName: str = None
		self._objectLibrary: str = None
		self._hasValidObj = False

	def set_object(self, objName: str, objLibrary: str = None) -> bool:
		if not self._reservedID:
			obj = try_get_object((objName, objLibrary))

			if obj == None:
				self._objectName = None
				self._objectLibrary = None
				self._hasValidObj = False
				return False
			else:
				self._objectName = objName
				self._objectLibrary = objLibrary
				self._hasValidObj = True
				return True
		else:
			print(f"Attempted to set object on {self} after it is already resolved.")