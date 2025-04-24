import Constants as C
import os
import base64
from Describers.Base import Describer
from io_ggltf.Core import Writer

class Buffer(Describer):
	def __init__(self):
		super().__init__()

		self._dataTypeHint = C.GLTF_BUFFER

		self._blob = bytearray()
		self._uri = None
		self._externalFileType = C.FILE_EXT_BIN
		self._name = None
		self._byteLength = 0

	def get_current_byte_lenght(self) -> int:
		return len(self._blob)
	
	def is_external(self) -> bool:
		return self._uri != None
	
	def _insert_bytes(self, bytes):
		if not self._isResovled:
			offset = len(self._blob)
			self._blob.append(bytes)
			return (offset, len(bytes))
		else:
			print("Attempted to add more bytes to buffer that is already resolved.")

	def _resolve(self, isBinary, gltfDict: dict, fileTargetPath: str) -> bool:
		external = self.is_external()

		id = self._get_id_reservation(gltfDict)
		bufferDict = {}

		if external:
			self._uri += self._externalFileType
			externalPath = os.path.join(os.path.dirname(fileTargetPath), self._uri)
			Writer.dump_raw_binary(externalPath, self._blob)
		elif isBinary:
			if C.__TEMP_INTERNAL_BUFFER in gltfDict:
				print("Attempted to add more then one internal buffer to a glb file.")
				self._isResolved = True
				return False
			gltfDict[C.__TEMP_INTERNAL_BUFFER] = self._blob
			self._isResolved = True
		else:
			bs64bytes = bytearray(base64.b64encode(self._blob))
			padAmount = len(bs64bytes) % 4
			if padAmount > 0:
				bs64bytes.append("=" * padAmount)

			self._uri = C.FILE_INTERNAL_BASE64_PREFIX + bs64bytes.decode("utf-8")
			
		if self._name != None and self._name != "":
			bufferDict[C.BUFFER_NAME] = self._name

		if self._uri != None:
			bufferDict[C.BUFFER_URI] = self._uri

		bufferDict[C.BUFFER_BYTE_LENGTH] = self.get_current_byte_lenght()

		gltfDict[C.GLTF_BUFFER][id] = bufferDict

		self._isResovled = True
		return True