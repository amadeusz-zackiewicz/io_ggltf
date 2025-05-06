from io_ggltf import Constants as C
from io_ggltf.Describers.Base import Describer
from io_ggltf.Describers.Buffer import BufferDescriber

class BufferViewDescriber(Describer):
	def __init__(self):
		super().__init__()

		self._dataTypeHint = C.GLTF_BUFFER_VIEW

		self._buffer: BufferDescriber = None
		self._byteOffset: int = 0
		self._byteLength: int = -1

	def set_buffer(self, buffer: BufferDescriber):
		if not self._isExported:
			self._buffer = buffer
		else:
			print("Attempted to set buffer on BufferView that is already exported.")

	def insert_bytes(self, bytes):
		if not self._isExported:
			if self._buffer == None:
				print("Attempted to insert bytes but no buffer was provided.")
				return 
			byteOffset, byteLenght = self._buffer.insert_bytes(bytes)
			self._byteOffset = byteOffset
			self._byteLength = byteLenght
		else:
			print("Attempted to insert bytes into exported BufferView.")


	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			if self._buffer == None:
				print("BufferView is missing a buffer.")
				self._isExported = True
				return False
			
			if self._byteLength == -1:
				print("BufferView has a target buffer but has no byte length.")
				self._isExported = True
				return False
			
			self._export_name()

			self._exportedData[C.BUFFER_VIEW_BUFFER] = self._buffer._get_id_reservation(gltfDict)
			self._exportedData[C.BUFFER_BYTE_LENGTH] = self._byteLength
			
			if self._byteOffset > 0:
				self._exportedData[C.BUFFER_VIEW_BYTE_OFFSET] = self._byteOffset

			

			self._isExported = True
			return True
		else:
			print("Attempted to export buffer view that is already exported.")
			return False