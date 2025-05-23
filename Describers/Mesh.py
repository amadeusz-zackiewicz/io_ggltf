from io_ggltf import Constants as C
from io_ggltf.Describers import *
from io_ggltf.Core.Scoops.Mesh import MeshUtil
from io_ggltf.Core.Util import try_get_object
from io_ggltf.Core import BlenderUtil, Util
from io_ggltf.Core.Validation import MeshValidation

class MeshDescriber(ObjectBasedDescriber):
	def __init__(self, buffer: BufferDescriber):
		super().__init__()

		self._dataTypeHint = C.GLTF_MESH

		self._originObjectName: str = None
		self._originObjLibrary: str = None
		self._hasValidOriginOverride: bool = False

		self._weights: list[float] = None

		self._buffer: BufferDescriber = buffer

		self._additionalObjectNames: list[str] = []
		self._additionalObjectLibraries: list[str] = []

		self._keepPose: bool = False

		self._skin: SkinDescriber = None
		self._boneInfluenceCount: int = 4

		self._floatPrecision: int = 7

		self._normals: bool = True
		self._tangets: bool = False
		self._vertexColors = False
		self._uvMaps = True

		self._shapeKeys = False
		self._shapeKeyIncludeNormals: bool = False
		self._shapeKeyIncludeUV: bool = False
		self._shapeKeyWeights: list[float] = None

	def set_origin_override(self, originObjName: str, originObjLibrary: str):
		if not self._isExported:
			obj = try_get_object((originObjName, originObjLibrary))

			if obj == None:
				self._originObjectName = None
				self._originObjLibrary = None
				self._hasValidOriginOverride = False
				print(f"Failed find object {originObjLibrary + '::' if originObjLibrary != None else ''}{originObjName}")
			else:
				self._originObjectName = originObjName
				self._originObjLibrary = originObjLibrary
				self._hasValidOriginOverride = True
		else:
			print(f"Attempted to set mesh origin override on {self} after it is already exported.")

	def set_buffer(self, buffer: BufferDescriber):
		if not self._isExported:
			self._buffer = buffer
		else:
			print(f"Attempted to change buffer of already exported mesh.")

	def set_normals(self, includeNormals: bool):
		if not self._isExported:
			self._normals = includeNormals
		else:
			print(f"Attempted to change normals of already exported mesh.")
	
	def set_tangets(self, includeTangets: bool):
		if not self._isExported:
			self._tangets = includeTangets
		else:
			print(f"Attempted to change tangets of already exported mesh.")

	def set_vertex_colors(self, includeVertexColors: bool | list[str]):
		if not self._isExported:
			self._vertexColors = includeVertexColors
		else:
			print(f"Attempted to change vertex colors of already exported mesh.")

	def set_uv_maps(self, includeUVs: bool | list[str]):
		if not self._isExported:
			self._uvMaps = includeUVs
		else:
			print(f"Attempted to change UV maps of already exported mesh.")

	def set_shape_keys(self, includeShapeKeys: bool | list[str], shapeKeysIncludeNormals: bool = False, shapeKeysIncludeUV: bool = False):
		if not self._isExported:
			self._shapeKeys = includeShapeKeys
			self._shapeKeyIncludeNormals = shapeKeysIncludeNormals
			self._shapeKeyIncludeUV = shapeKeysIncludeUV
		else:
			print(f"Attempted to change shape keys of already exported mesh.")

	def merge_mesh(self, meshObjName: str, meshObjLibrary: str = None):
		if not self._isExported:
			obj = try_get_object((meshObjName, meshObjLibrary))

			if obj == None:
				print(f"Failed to get object: {meshObjLibrary + '::' if meshObjLibrary != None else ''}{meshObjName}")

			if BlenderUtil.object_is_meshlike(obj):
				self._additionalObjectNames.append(meshObjName)
				self._additionalObjectLibraries.append(meshObjLibrary)
			else:
				print(f"Object {meshObjLibrary + '::' if meshObjName != None else ''}{meshObjName} is of type {obj.type}, expected type: {C.BLENDER_TYPE_MESH}")
		else:
			print("Attempted to merge meshes with an already exported mesh.")

	def __get_all_objects(self) -> list:
		objects = []

		if self._hasValidObject:
			obj = try_get_object((self._objectName, self._objectLibrary))
			if BlenderUtil.object_is_meshlike(obj):
				objects.append(obj)

		for i in range(len(self._additionalObjectNames)):
			obj = try_get_object((self._additionalObjectNames[i], self._additionalObjectLibraries[i]))
			if obj != None:
				objects.append(obj)
			else:
				print(f"Failed to find mesh object: {self._additionalObjectLibraries[i] + '::' if self._additionalObjectLibraries[i] != None else ''}{self._additionalObjectNames[i]}")

		return objects
		
	def __get_material_id_map(self, meshObjects) -> dict[str, int]:
		materialNames = set()
		for meshObject in meshObjects:
			for materialSlot in meshObject.material_slots:
				materialNames.add(materialSlot.name)

		materialMap = {}
		for i, materialName in enumerate(materialNames):
			materialMap[materialName] = i

		return materialMap

	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			if not self._hasValidObject:
				print("No valid object set for mesh export.")
				self._isExported = True
				return False
			
			meshObjects = self.__get_all_objects()

			if type(self._uvMaps) == list:
				MeshValidation.objects_have_uv_maps(meshObjects, self._uvMaps)
			if type(self._vertexColors) == list:
				MeshValidation.objects_have_vertex_colors(meshObjects, self._vertexColors)
			if type(self._shapeKeys) == list:
				MeshValidation.objects_have_shape_keys(meshObjects, self._shapeKeys)

			if self._hasValidOriginOverride:
				targetMatrix = try_get_object((self._originObjectName, self._originObjLibrary)).world_matrix
			else:
				targetMatrix = meshObjects[0].matrix_world
			
			if self._skin != None and self._boneInfluenceCount > 0:
				if not self._skin._isExported:
					self._skin._export(isBinary, gltfDict, fileTargetPath)

			depsGraph = BlenderUtil.get_depsgraph()
			materialIDMap = self.__get_material_id_map(meshObjects)
			meshesInFlight = [None] * len(meshObjects)

			for iMeshObj, meshObject in enumerate(meshObjects):
				mesh = MeshInFlight()
				mesh.set_object(meshObject, depsGraph, targetMatrix, self._keepPose)
				mesh.set_materials_remap(materialIDMap)
				mesh.sample_loop_positions()
				if self._normals:
					mesh.sample_loop_normals()
				if self._tangets:
					mesh.sample_loop_tangents()
				if self._uvMaps:
					mesh.sample_loop_uvs(self._uvMaps)
				if self._vertexColors:
					mesh.sample_loop_colors(self._vertexColors)
				if self._shapeKeys:
					mesh.sample_shape_key_positions(self._shapeKeys)
				if self._skin != None and self._boneInfluenceCount > 0:
					mesh.sample_loop_weights(self._skin._skinDefinition, self._boneInfluenceCount)

				# TODO: extension: on mesh sample here
				

				mesh.vertexData, mesh.triangles, mesh.trianglesMaterialIndex = MeshUtil.get_indexed_triangles(mesh.loopsData, mesh.mesh, mesh.materialIDRemap)
				mesh.clean_up()

				meshesInFlight[iMeshObj] = mesh

			exportPrimitives = ExportedPrimitives(meshesInFlight, materialIDMap, self._buffer, self._floatPrecision, gltfDict, fileTargetPath, isBinary)
			exportPrimitives.export()

			self._export_name()
			self._exportedData[C.MESH_PRIMITIVES] = exportPrimitives.bakedPrimitives

			self._isExported = True
			return True
		else:
			print(f"Tried to export mesh that was already exported.")
			return False
		


class MeshInFlight():
	def __init__(self):
		self.obj = None
		self.mesh = None

		self.keepPose: bool = False
		self.objModifierResetArray: list[bool] = []

		self.depsGraph = None

		self.mode = C.MESH_TYPE_TRIANGLES
		self.materialIDRemap: list[int] = []

		self.vertexGroups = None

		# data map
		self.arrayPositions: int = -1
		self.arrayNormals: int = -1
		self.arrayTangent: int = -1
		self.arraysColors: list[int] = []
		self.arraysUVMaps: list[int] = []
		self.arrayBoneIDs: int = -1
		self.arrayBoneWeights: list[int] = []
		self.arraysShapeKeyPositions: list[int] = []

		self.triangles: list[list[int]] = None
		self.trianglesMaterialIndex: list[int] = []

		self.vertexData: list[list] = []
		self.loopsData: list[list] = []

	def set_object(self, obj, depsGraph, originWorldMatrix, keepPose: bool = False):
		self.obj = obj
		self.depsGraph = depsGraph
		self.keepPose = keepPose

		if not keepPose:
			self.objModifierResetArray = BlenderUtil.get_all_mod_states(obj)
			BlenderUtil.batch_set_modifier_type(obj, C.BLENDER_MODIFIER_ARMATURE, False)
			depsGraph.update()

		self.mesh = depsGraph.id_eval_get(obj).to_mesh()

		if obj.matrix_world != originWorldMatrix:
			self.mesh.transform(obj.matrix_world, shape_keys=True)
			self.mesh.transform(originWorldMatrix, shape_keys=True)
			self.mesh.update()

	def set_materials_remap(self, materialDict: dict[str, int]):
		materialSlots = self.obj.material_slots
		self.materialIDRemap = [0] * len(materialSlots)

		for iSlot, materialSlot in enumerate(materialSlots):
			self.materialIDRemap[iSlot] = materialDict.get(materialSlot.name, 0)

	def sample_loop_positions(self):
		self.arrayPositions = len(self.loopsData)
		self.loopsData.append(MeshUtil.extract_loop_positions(self.mesh))

	def sample_loop_normals(self):
		self.arrayNormals = len(self.loopsData)
		self.loopsData.append(MeshUtil.extract_loop_normals(self.mesh))

	def sample_loop_tangents(self):
		self.arrayTangent = len(self.loopsData)
		self.loopsData.append(MeshUtil.extract_loop_tangets(self.mesh))

	def sample_loop_colors(self, includeVertexColors: bool | list[str]):
		startID = len(self.loopsData)
		self.loopsData += MeshUtil.extract_loop_colors(includeVertexColors)
		self.arraysColors = list(range(startID, len(self.loopsData)))

	def sample_loop_uvs(self, includeUVmaps: bool | list[str]):
		startID = len(self.loopsData)
		self.loopsData += MeshUtil.extract_loop_uv_maps(self.mesh, includeUVmaps)
		self.arraysUVMaps = list(range(startID, len(self.loopsData)))

	def sample_loop_weights(self, skinDefinition: dict, maxBoneInfluences: int = 4):
		jointIDArray, boneWeightArray = MeshUtil.extract_loop_bone_weights(self.obj, self.mesh, skinDefinition, maxBoneInfluences)
		self.arrayBoneIDs = len(self.loopsData)
		self.loopsData.append(jointIDArray)
		self.arrayBoneWeights = len(self.loopsData)
		self.loopsData.append(boneWeightArray)

	def sample_shape_key_positions(self, includeShapeKeys: bool | list[str]):
		startID = len(self.loopsData)
		self.loopsData += MeshUtil.extract_loop_shape_keys(self.mesh, includeShapeKeys)
		self.arraysShapeKeyPositions = list(range(startID, len(self.loopsData)))

	def clean_up(self):
		if not self.keepPose:
			BlenderUtil.batch_set_modifiers(self.obj, self.objModifierResetArray)
			self.depsGraph.update()
		self.mesh = None
		self.obj.to_mesh_clear()


class ExportedPrimitives():
	def __init__(self, meshes: list[MeshInFlight], materials: dict, bufferDescriber: BufferDescriber, floatPrecision: int, gltfDict: dict, targetFilePath: str, isBinary: bool):
		self.meshes = meshes
		self.bakedPrimitives: list[dict] = []
		self.materials: dict = materials
		self.buffer: BufferDescriber = bufferDescriber
		self.floatPrecision: int = 7
		self.gltfDict: dict = gltfDict
		self.targetFilePath: str = targetFilePath
		self.isBinary: bool = isBinary

	def export(self):
		meshPerMaterial: list[MeshInFlight] = []

		for _ in range(max(len(self.materials), 1)): # make at least 1 mesh
			mesh = MeshInFlight()
			mesh.arrayPositions = self.meshes[0].arrayPositions
			mesh.arrayNormals = self.meshes[0].arrayNormals
			mesh.arrayTangent = self.meshes[0].arrayTangent
			mesh.arraysColors = self.meshes[0].arraysColors
			mesh.arraysUVMaps = self.meshes[0].arraysUVMaps
			mesh.arrayBoneIDs = self.meshes[0].arrayBoneIDs
			mesh.arrayBoneWeights = self.meshes[0].arrayBoneWeights
			mesh.arraysShapeKeyPositions = self.meshes[0].arraysShapeKeyPositions

			mesh.vertexData = []
			mesh.triangles = []

			for _ in range(len(self.meshes[0].vertexData)):
				mesh.vertexData.append([])

			meshPerMaterial.append(mesh)

		if self.meshes[0].mode == C.MESH_TYPE_TRIANGLES:
			self.__indexed_triangles_export(meshPerMaterial)

	def __indexed_triangles_transfer_by_material_id(self, fromMeshes: list[MeshInFlight], toMeshes: list[MeshInFlight]):
		from collections import OrderedDict
		for iFromMesh, fromMesh in enumerate(fromMeshes):
			duplicates: list[OrderedDict] = []
			for _ in range(len(toMeshes)):
				duplicates.append(OrderedDict())

			for iFromTriangle, fromTriangle in enumerate(fromMesh.triangles):
				iToMesh = fromMesh.trianglesMaterialIndex[iFromTriangle]
				toMesh = toMeshes[iToMesh]
				newTriangle = [-1, -1, -1]

				for i in range(3):
					if fromTriangle[i] in duplicates[iToMesh]:
						newTriangle[i] = duplicates[iToMesh][fromTriangle[i]]
					else:
						duplicates[iToMesh][fromTriangle[i]] = len(toMesh.vertexData[0])
						newTriangle[i] = len(toMesh.vertexData[0])
						for iData, vData in enumerate(fromMesh.vertexData):
							toMesh.vertexData[iData].append(vData[fromTriangle[i]])
				toMesh.triangles.append(newTriangle)

	def __indexed_triangles_export(self, meshPerMaterial: list[MeshInFlight]):
		self.__indexed_triangles_transfer_by_material_id(self.meshes, meshPerMaterial)

		for mesh in meshPerMaterial:
			mesh.vertexData, mesh.triangles = MeshUtil.optimise_indexed_triangles(mesh.vertexData, mesh.triangles)

		self.meshes = meshPerMaterial

		self.__indexed_triangles_to_dicts()

	def __indexed_triangles_to_dicts(self):
		for mesh in self.meshes:
			primtiveDict = {C.MESH_PRIMITIVE_MODE: C.MESH_TYPE_TRIANGLES, }

			targets = self.__export_targets(mesh)
			if len(targets) > 0:
				primtiveDict[C.MESH_PRIMITIVE_TARGETS] = targets

			primtiveDict[C.MESH_PRIMITIVE_INDICES] = self.__export_indexed_triangles_indices(mesh.triangles, len(mesh.vertexData[0]))

			attributes: dict[str, int] = {}

			if mesh.arrayPositions != -1:
				attributes[C.MESH_ATTRIBUTE_STR_POSITION] = self.__export_positions(mesh.vertexData[mesh.arrayPositions])
			if mesh.arrayNormals != -1:
				attributes[C.MESH_ATTRIBUTE_STR_NORMAL] = self.__export_normals(mesh.vertexData[mesh.arrayNormals])
			if mesh.arrayTangent != -1:
				attributes[C.MESH_ATTRIBUTE_STR_TANGENT] = self.__export_tangents(mesh.vertexData[mesh.arrayTangent])
			if len(mesh.arraysColors) > 0:
				self.__export_vertex_colors(attributes, [mesh.vertexData[i] for i in mesh.arraysColors])
			if len(mesh.arraysUVMaps) > 0:
				self.__export_uv_maps(attributes, [mesh.vertexData[i] for i in mesh.arraysUVMaps])
			if mesh.arrayBoneIDs != -1 and mesh.arrayBoneWeights != -1:
				self.__export_joints(attributes, mesh.vertexData[mesh.arrayBoneIDs], mesh.vertexData[mesh.arrayBoneWeights])

			primtiveDict[C.MESH_PRIMITIVE_ATTRIBUTES] = attributes

			self.bakedPrimitives.append(primtiveDict)

	def __export_accessor(self, accessor: AccessorDescriber) -> int:
		accessorID = accessor._get_id_reservation(self.gltfDict)
		bufferView = accessor._bufferView
		bufferViewID = bufferView._get_id_reservation(self.gltfDict)

		self.gltfDict[C.GLTF_ACCESSOR][accessorID] = accessor._exportedData
		self.gltfDict[C.GLTF_BUFFER_VIEW][bufferViewID] = bufferView._exportedData

		accessor._export(self.isBinary, self.gltfDict, self.targetFilePath)
		return accessorID

	def __export_indexed_triangles_indices(self, data, vertexCount: int):

		if vertexCount > 65000:
			packingFormat = C.PACKING_FORMAT_U_INT
			componentType = C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_INT
		else:
			packingFormat = C.PACKING_FORMAT_U_SHORT
			componentType = C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT

		accessor = AccessorDescriber()
		accessor.set_float_precision(self.floatPrecision)
		flattenedData = [-1] * len(data * 3)
		for i, d in enumerate(data):
			for j in range(3):
				flattenedData[int(i * 3) + j] = d[j]

		accessor.insert_data(flattenedData, 
					   self.buffer, 
					   C.ACCESSOR_TYPE_SCALAR, 
					   componentType, 
					   packingFormat)

		return self.__export_accessor(accessor)

	def __export_positions(self, data) -> int:
		accessor = AccessorDescriber()
		accessor.set_float_precision(self.floatPrecision)

		_max = [-10000.0, -10000.0, -10000.0]
		_min = [10000.0, 10000.0, 10000.0]

		for d in data:
			for i in range(3):
				_max[i] = max(_max[i], d[i])
				_min[i] = min(_min[i], d[i])

		Util.round_float_list_to_precision(_max, self.floatPrecision)
		Util.round_float_list_to_precision(_min, self.floatPrecision)

		accessor.insert_data(data, 
					   self.buffer, 
					   C.ACCESSOR_TYPE_VECTOR_3, 
					   C.ACCESSOR_COMPONENT_TYPE_FLOAT,
					   C.PACKING_FORMAT_FLOAT,
					   _max, _min)
		
		return self.__export_accessor(accessor)
	
	def __export_normals(self, data) -> int:
		accessor = AccessorDescriber()
		accessor.set_float_precision(self.floatPrecision)

		accessor.insert_data(data,
					   self.buffer,
					   C.ACCESSOR_TYPE_VECTOR_3,
					   C.ACCESSOR_COMPONENT_TYPE_FLOAT,
					   C.PACKING_FORMAT_FLOAT)
		
		return self.__export_accessor(accessor)
	
	def __export_tangents(self, data) -> int:
		accessor = AccessorDescriber()
		accessor.set_float_precision(self.floatPrecision)

		accessor.insert_data(data,
					   self.buffer,
					   C.ACCESSOR_TYPE_VECTOR_4,
					   C.ACCESSOR_COMPONENT_TYPE_FLOAT,
					   C.PACKING_FORMAT_FLOAT)

		return self.__export_accessor(accessor)
	
	def __export_uv_maps(self, attributes: dict[str, int], data:list[list]):
		for i, d in enumerate(data):
			attrName = C.MESH_ATTRIBUTE_STR_TEXCOORD + str(i)
			accessor = AccessorDescriber()
			accessor.set_float_precision(self.floatPrecision)
			accessor.insert_data(d,
						self.buffer,
						C.ACCESSOR_TYPE_VECTOR_2,
						C.ACCESSOR_COMPONENT_TYPE_FLOAT,
						C.PACKING_FORMAT_FLOAT)
			
			attributes[attrName] = self.__export_accessor(accessor)

	def __export_vertex_colors(self, attributes: dict[str, int], data: list[list]):
		for i, d in enumerate(data):
			attrName = C.MESH_ATTRIBUTE_STR_COLOR + str(i)

			accessor = AccessorDescriber()
			accessor.set_float_precision(self.floatPrecision)
			accessor.insert_data(d,
						self.buffer,
						C.ACCESSOR_TYPE_VECTOR_4,
						C.ACCESSOR_COMPONENT_TYPE_FLOAT,
						C.PACKING_FORMAT_FLOAT)
			
			attributes[attrName] = self.__export_accessor(accessor)

	def __export_joints(self, attributes: dict[str, int], boneIDdata: list[list[int]], boneWeightData: list[list[float]]):
		divisions = int(len(boneIDdata[0]) / 4)
		for i in range(divisions):
			attrNameJoint = C.MESH_ATTRIBUTE_STR_JOINT + str(i)
			attrNameWeights = C.MESH_ATTRIBUTE_STR_WEIGHT + str(i)

			slicedMin = i * 4
			slicedMax = (i + 1) * 4

			slicedIDs = [boneIDs[slicedMin:slicedMax] for boneIDs in boneIDdata]
			slicedWeights = [weights[slicedMin:slicedMax] for weights in boneWeightData]

			jointAccessor = AccessorDescriber()
			weightAccessor = AccessorDescriber()
			weightAccessor.set_float_precision(self.floatPrecision)

			jointAccessor.insert_data(slicedIDs,
							 self.buffer,
							 C.ACCESSOR_TYPE_VECTOR_4,
							 C.ACCESSOR_COMPONENT_TYPE_UNSIGNED_SHORT,
							 C.PACKING_FORMAT_U_SHORT)
			weightAccessor.insert_data(slicedWeights,
							  self.buffer,
							  C.ACCESSOR_TYPE_VECTOR_4,
							  C.ACCESSOR_COMPONENT_TYPE_FLOAT,
							  C.PACKING_FORMAT_FLOAT)

			attributes[attrNameJoint] = self.__export_accessor(jointAccessor)
			attributes[attrNameWeights] = self.__export_accessor(weightAccessor)

	def __export_targets(self, mesh: MeshInFlight) -> list[dict]:
		if len(mesh.arraysShapeKeyPositions) == 0: #TODO: add checks for normals and UVs
			return []
		
		targets: list[dict] = [{} for _ in range(len(mesh.arraysShapeKeyPositions))]

		for targetID, arrayID in enumerate(mesh.arraysShapeKeyPositions):
			accessor = AccessorDescriber()
			accessor.set_float_precision(self.floatPrecision)
			accessor.insert_data(mesh.vertexData[arrayID],
						self.buffer,
						C.ACCESSOR_TYPE_VECTOR_3,
						C.ACCESSOR_COMPONENT_TYPE_FLOAT,
						C.PACKING_FORMAT_FLOAT)
			targets[targetID][C.MESH_ATTRIBUTE_STR_POSITION] = self.__export_accessor(accessor)
		
		# TODO: normals
		# TODO: uvs

		return targets