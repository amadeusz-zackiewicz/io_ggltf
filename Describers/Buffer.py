import os
import base64
from io_ggltf import Constants as C
from io_ggltf.Describers.Base import Describer
from io_ggltf.Core import Writer

class BufferDescriber(Describer):
	def __init__(self, URI: str = None):
		super().__init__()

		self._dataTypeHint = C.GLTF_BUFFER

		self._blob: bytearray = bytearray()
		self._uri: str = URI
		self._externalFileType = C.FILE_EXT_BIN
		self._name: str = None
		self._byteLength: int = 0

	def get_current_byte_lenght(self) -> int:
		return len(self._blob)
	
	def is_external(self) -> bool:
		return self._uri != None
	
	def insert_bytes(self, bytes):
		if not self._isExported:
			offset = len(self._blob)
			self._blob.extend(bytes)
			return (offset, len(bytes))
		else:
			print("Attempted to add more bytes to buffer that is already exported.")

	def _export(self, isBinary, gltfDict: dict, fileTargetPath: str) -> bool:
		if not self._isExported:
			external = self.is_external()

			id = self._get_id_reservation(gltfDict)

			if external:
				self._uri += self._externalFileType
				externalPath = os.path.join(os.path.dirname(fileTargetPath), self._uri)
				Writer.dump_raw_binary(externalPath, self._blob)
			elif isBinary:
				if C.GLB_TEMP_INTERNAL_BUFFER in gltfDict:
					print("Attempted to add more then one internal buffer to a glb file.")
					self._isExported = True
					return False
				gltfDict[C.GLB_TEMP_INTERNAL_BUFFER] = self._blob
			else:
				bs64bytes = bytearray(base64.b64encode(self._blob))
				padAmount = len(bs64bytes) % 4
				if padAmount > 0:
					bs64bytes.append("=" * padAmount)

				self._uri = C.FILE_INTERNAL_BASE64_PREFIX + bs64bytes.decode("utf-8")
				
			self._export_name()

			if self._uri != None and self._uri != "":
				self._exportedData[C.BUFFER_URI] = self._uri

			self._exportedData[C.BUFFER_BYTE_LENGTH] = self.get_current_byte_lenght()

			self._isExported = True
			return True
		else:
			print("Attempted to export buffer that is already exported.")
			return False