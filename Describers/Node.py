import mathutils
from io_ggltf import Constants as C
from io_ggltf.Describers.Base import ObjectBasedDescriber, Describer
from io_ggltf.Core import Util
from io_ggltf.Core.BlenderUtil import get_object_accessor


class NodeDescriber(ObjectBasedDescriber):
	def __init__(self):
		super().__init__()

		self._dataTypeHint = C.GLTF_NODE

		self._children: list[NodeDescriber] = []
		self._skin: Describer = None
		self._mesh: Describer = None
		self._camera: Describer = None
		self._name: str = None
		self._translation: list[float] = None
		self._rotation: list[float] = None
		self._scale: list[float] = None
		self._matrix: list[float] = None
		self._weights: list[float] = None

		self._useMatrix: bool = False
		self._parent: NodeDescriber = None
		self._floatPrecision: int = 6
		self._scaleCorrection: float = 0.000002

	def set_parent(self, parent: Describer):
		if not self._isExported:
			self._parent = parent
		else:
			print("Attempted to set parent of a node that is already exported.")
		
	def append_child(self, child: Describer):
		if not self._isExported:
			child._parent = self
			self._children.append(child)
		else:
			print("Attempted to append a child to a node that is already exported.")
			return False
		
	def set_float_precision(self, precision: float):
		if not self._isExported:
			self._floatPrecision = precision
		else:
			print("Attempted to set float precision on a node that is already exported.")
			return False
		
	def set_scale_correction(self, errorTolerance: float):
		if not self._isExported:
			self._scaleCorrection = errorTolerance
		else:
			print("Attempted to set scale correction on a node that is already exported.")
			return False
		
	def set_translation(self, x: float, y: float, z: float, yUp: bool = True):
		if not self._isExported:
			if yUp:
				self._translation = [x, y, z]
			else:
				self._translation = Util.y_up_location([x, y, z])
		else:
			print("Attempted to change translation of already exported node")

	def set_rotation(self, x: float, y: float, z: float, yUp: bool = True):
		if not self._isExported:
			quat = mathutils.Euler([x, y, z]).to_quaternion()
			if yUp:
				self._rotation = Util.bl_math_to_gltf_list(quat)
			else:
				self._rotation = Util.bl_math_to_gltf_list(Util.y_up_rotation(quat))
		else:
			print("Attempted to change rotation of already exported node")

	def set_scale(self, x: float, y: float, z: float, yUp: bool = True):
		if not self._isExported:
			if yUp:
				self._scale = [x, y, z]
			else:
				self._scale = Util.y_up_scale([x, y, z])
		else:
			print("Attempted to change scale of already exported node")
		
	def __export_children(self, isBinary, gltfDict, fileTargetPath) -> bool:
		for child in self._children:
			if not child._isExported:
				if not child._export(isBinary, gltfDict, fileTargetPath):
					return False
				
			self._exportedData[C.NODE_CHILDREN].append(child._get_id_reservation(gltfDict))

	def __export_translation(self, translation):
		if translation != None:
			t = Util.bl_math_to_gltf_list(translation)
			Util.round_float_list_to_precision(t, self._floatPrecision)
			if t[0] == 0.0 and t[1] == 0.0 and t[2] == 0.0:
				pass
			else: 
				self._exportedData[C.NODE_TRANSLATION] = t

	def __export_rotation(self, rotation):
		if rotation != None:
			r = Util.bl_math_to_gltf_list(rotation)
			Util.round_float_list_to_precision(r, self._floatPrecision)
			if r[0] == 0.0 and r[1] == 0.0 and r[2] == 0.0 and r[3] == 1.0:
				pass
			else:
				self._exportedData[C.NODE_ROTATION] = r

	def __export_scale(self, scale):
		if scale != None:
			s = Util.bl_math_to_gltf_list(scale)

			for i in range(3):
				if abs(s[i] - 1.0) <= self._scaleCorrection:
					if s[i] < 0.0:
						s[i] = -1.0
					else:
						s[i] = 1.0

			Util.round_float_list_to_precision(s, self._floatPrecision)
	
			if s[0] == 1.0 and s[1] == 1.0 and s[2] == 1.0:
				pass
			else:
				self._exportedData[C.NODE_SCALE] = s

	def __export_matrix(self, matrix):
		if matrix != None:
			m = Util.bl_math_to_gltf_list(matrix)
			Util.round_float_list_to_precision(m, self._floatPrecision)
			writeRequired = False

			for i in [0, 5, 10, 15]:
				if m[i] != 1.0:
					writeRequired = True
					break

			for i in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14]:
				if m[i] != 0.0:
					writeRequired = True
					break
			
			if writeRequired:
				self._exportedData[C.NODE_MATRIX] = m

	def __export_weights(self, weights):
		if weights != None:
				self._exportedData[C.NODE_WEIGHTS] = weights

	def __export_mesh(self, gltfDict) -> list:
		return None
		
	def __export_skin(self, gltfDict):
		pass

	def __export_camera(self, gltfDict):
		pass

	def _export(self, isBinary, gltfDict, fileTargetPath) -> bool:
		if not self._isExported:

			self._export_name()

			boneTuple = (self._objectName, self._objectLibrary, self._boneName)
			objTuple = (self._objectName, self._objectLibrary)

			parentTuple = None
			if self._parent != None:
				parent = self._parent
				if parent._boneName != None:
					parentTuple = (parent._objectName, parent._objectLibrary, parent._boneName)
				else:
					parentTuple = (parent._objectName, parent._objectLibrary)
				
			if self._useMatrix:
				if Util.try_get_bone(boneTuple) != None:
					converted, matrix = Util.evaluate_matrix(boneTuple, parentTuple)
				else:
					converted, matrix = Util.evaluate_matrix(objTuple, parentTuple)
				if not converted:
					matrix = Util.y_up_matrix(matrix)

				self.__export_matrix(matrix if self._matrix == None else self._matrix)
			else:
				if Util.try_get_bone(boneTuple) != None:
					translation, rotation, scale = Util.get_yup_transforms(boneTuple, parentTuple)
				else:
					translation, rotation, scale = Util.get_yup_transforms(objTuple, parentTuple)

				self.__export_translation(translation if self._translation == None else self._translation)
				self.__export_rotation(rotation if self._rotation == None else self._rotation)
				self.__export_scale(scale if self._scale == None else self._scale)
			

			if len(self._children) > 0:
				childrenIDs = []
				for c in self._children:
					childrenIDs.append(self._get_id_reservation(gltfDict))

				self._exportedData[C.NODE_CHILDREN] = childrenIDs
			
			weights = self.__export_mesh(gltfDict)
			self.__export_camera(gltfDict)
			self.__export_skin(gltfDict)

			self.__export_weights(weights)

			self._isExported = True
			return True
		else:
			print("Attempted to export a node that is already exported.")
			return False
		

def FromObject(objectName: str = None, objectLibrary: str = None, boneName: str = None) -> NodeDescriber:
	describer = NodeDescriber()
	describer.set_target(objName=objectName, objLibrary=objectLibrary, boneName=boneName)
	if describer._hasValidObject:
		return describer
	else:
		if objectLibrary != None:
			if boneName != None:
				print(f"Failed to find target: {objectLibrary}::{objectName}.bones[{boneName}]")
			else:
				print(f"Failed to find target: {objectLibrary}::{objectName}")
		else:
			if boneName != None:
				print(f"Failed to find target: {objectName}.bones[{boneName}]")
			else:
				print(f"Failed to find target: {objectName}")
		return None

