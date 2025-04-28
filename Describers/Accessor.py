import struct
import mathutils
from io_ggltf import Constants as C
from io_ggltf.Describers.Base import Describer
from io_ggltf.Describers.BufferView import BufferViewDescriber
from io_ggltf.Describers.Buffer import BufferDescriber
from io_ggltf.Core import Util

class AccessorDescriber(Describer):
	def __init__(self):
		super().__init__()

		self._dataTypeHint = C.GLTF_ACCESSOR

		self._floatPrecision: int = 7
		self._componentType: int = -1
		self._count: int = -1
		self._type: str = None
		self._max = None
		self._min = None
		self._bufferView: BufferViewDescriber = None
		self._byteOffset: int = 0

		self.__VECTOR_TYPES = [C.ACCESSOR_TYPE_VECTOR_2, C.ACCESSOR_TYPE_VECTOR_3, C.ACCESSOR_TYPE_VECTOR_4]
		self.__MATRIX_TYPES = [C.ACCESSOR_TYPE_MATRIX_2, C.ACCESSOR_TYPE_MATRIX_3, C.ACCESSOR_TYPE_MATRIX_4]
		self.__SCALAR_TYPES = [C.ACCESSOR_TYPE_SCALAR]

		self.__vector_types = [None, None, C.ACCESSOR_TYPE_VECTOR_2, C.ACCESSOR_TYPE_VECTOR_3, C.ACCESSOR_TYPE_VECTOR_4]
		self.__matrix_types = [None, None, C.ACCESSOR_TYPE_MATRIX_2, C.ACCESSOR_TYPE_MATRIX_3, C.ACCESSOR_TYPE_MATRIX_4]

	def __guess_grouping_type(self, data: list):
		typeOf = type(data[0])
		if typeOf == int or typeOf == float or typeOf == bool:
			return C.ACCESSOR_TYPE_SCALAR
		if typeOf == mathutils.Vector:
			length = len(data[0])
			try: return self.__vector_types[length]
			except: return None
		if typeOf == mathutils.Quaternion:
			return C.ACCESSOR_TYPE_VECTOR_4
		if typeOf == mathutils.Matrix:
			row = len(data[0])
			col = len(data[0][0])
			if row != col: return None
			return self.__matrix_types[row]
	
	def __guess_component_type(self, data: list):
		typeOf = type(data[0])
		if typeOf == mathutils.Vector:
			if type(data[0][0]) == float:
				return C.ACCESSOR_COMPONENT_TYPE_FLOAT
			if type(data[0][0]) == int:
				return C.ACCESSOR_COMPONENT_TYPE_SHORT
		if typeOf == float or typeOf == mathutils.Quaternion or typeOf == mathutils.Matrix:
			return C.ACCESSOR_COMPONENT_TYPE_FLOAT
		if typeOf == int:
			return C.ACCESSOR_COMPONENT_TYPE_SHORT
		if typeOf == bool:
			return C.ACCESSOR_COMPONENT_TYPE_BYTE
	
	def __guess_packing_format(self, data: list):
		typeOf = type(data[0])
		if typeOf == mathutils.Vector:
			if type(data[0][0]) == float:
				return C.PACKING_FORMAT_FLOAT
			if type(data[0][0]) == int:
				return C.PACKING_FORMAT_SHORT
		if typeOf == float or typeOf == mathutils.Quaternion or typeOf == mathutils.Matrix:
			return C.PACKING_FORMAT_FLOAT
		if typeOf == int:
			return C.PACKING_FORMAT_SHORT
		if typeOf == bool:
			return C.PACKING_FORMAT_BOOL
		
	def __scalar_into_bytearray(self, _format, data: list):
		size = struct.calcsize(_format)
		_bytes = bytearray(size * len(data))
		st = struct.Struct(_format)

		if type(data[0]) == float and self._floatPrecision >= 0:
			Util.round_float_list_to_precision(data, self._floatPrecision) 

		for i, s in enumerate(data):
			st.pack_into(_bytes, i * size, s)

		return _bytes
	
	def __flatten_vectors(self, format, data: list):
		scalar = []

		if type(data[0]) == mathutils.Quaternion:
			for q in data:
				scalar.extend(Util.bl_math_to_gltf_list(q))
		else:
			for v in data:
				for f in v:
					scalar.append(f)

		return self.__scalar_into_bytearray(format, scalar)
	
	def __flatten_matrices(self, format, data: list):
		rowSize = len(data[0].row[0])
		colSize = len(data[0].col[0])

		scalar = []

		for m in data:
			for r in range(rowSize):
				for c in range(colSize):
					scalar.append(m[r][c])

		return self.__scalar_into_bytearray(format, scalar)

	def set_float_precision(self, precision: int):
		if not self._isExported:
			self._floatPrecision = precision
		else:
			print("Attempted to set float precision on accessor that is already exported.")

	def insert_data(self, data: list, buffer: BufferDescriber, groupingType = None, componentType = None, packingFormat = None, max = None, min = None):
		if not self._isExported:
			if self._bufferView != None:
				print("Accessor already has data set and cannot accept new data.")
				return
			
			if groupingType == None:
				groupingType = self.__guess_grouping_type(data)
			if componentType == None:
				componentType = self.__guess_component_type(data)
			if packingFormat == None:
				packingFormat = self.__guess_packing_format(data)

			self._type = groupingType
			self._componentType = componentType
			self._count = len(data)

			if min != None:
				self._min = min
			if max != None:
				self._max = max

			bytes = None

			if groupingType in self.__VECTOR_TYPES:
				bytes = self.__flatten_vectors(packingFormat, data)
			elif groupingType in self.__MATRIX_TYPES:
				bytes = self.__flatten_matrices(packingFormat, data)
			elif groupingType in self.__SCALAR_TYPES:
				bytes = self.__scalar_into_bytearray(packingFormat, data)
			else:
				bytes = bytearray()

			if len(bytes) == 0:
				print("Accessor failed to convert data to bytearray.")

			bufferView = BufferViewDescriber()
			bufferView.set_buffer(buffer)
			bufferView.insert_bytes(bytes)

			self._bufferView = bufferView

		else:
			print("Attempted to set data on accessor that is already exported.")
		
	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			if self._bufferView == None:
				print("Accessor is missing a bufferView.")
				self._isExported = True
				return False
			
			self._export_name()

			if self._byteOffset != 0:
				self._exportedData[C.ACCESSOR_BYTE_OFFSET] = self._byteOffset
			self._exportedData[C.ACCESSOR_COMPONENT_TYPE] = self._componentType
			self._exportedData[C.ACCESSOR_COMPONENT_TYPE] = self._type
			self._exportedData[C.ACCESSOR_COUNT] = self._count

			if self._max != None:
				self._exportedData[C.ACCESSOR_MAX] = self._max
			if self._min != None:
				self._exportedData[C.ACCESSOR_MIN] = self._min

			self._exportedData[C.ACCESSOR_BUFFER_VIEW] = self._bufferView._get_id_reservation(gltfDict)
			
			self._bufferView._export(isBinary, gltfDict, fileTargetPath)

			self._isExported = True
			return True
		else:
			print("Attempted to export accessor that is already exported.")
			return False
	