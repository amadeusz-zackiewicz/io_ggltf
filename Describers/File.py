import os
import bpy
import json
import re
import struct
from io_ggltf import Constants as C
from io_ggltf.Describers.Base import Describer
from io_ggltf.Describers.Scene import Scene as SceneDescriber
from io_ggltf.Core import Util

class File(Describer):
	def __init__(self, fileDirectory: str, fileName: str, binary: bool = True):
		super().__init__()

		self._name = fileName
		self._fileDirectory: str = fileDirectory
		self._isBinary: str = binary
		self._enforceDefaultScene: bool = True
		self._catchStrayNodes: bool = True
		self._defaultScene: SceneDescriber = None
		self._jsonSeparator = (",", ":")

		self._describersMap = {
			C.GLTF_SCENE : [],
			C.GLTF_NODE : [],
			C.GLTF_CAMERA : [],
			C.GLTF_SKIN : [],
			C.GLTF_MESH : [],
			C.GLTF_MATERIAL : [],
			C.GLTF_TEXTURE : [],
			C.GLTF_IMAGE : [],
			C.GLTF_SAMPLER : [],
			C.GLTF_ANIMATION : [],
			C.GLTF_ACCESSOR : [],
			C.GLTF_BUFFER_VIEW : [],
			C.GLTF_BUFFER : []
		}

	def set_file_directory(self, fileDirectory: str):
		if not self._isExported:
			self._fileDirectory = fileDirectory
		else:
			print("Attempted to change file directory of already exported file.")

	def get_file_directory(self) -> str:
		return self._fileDirectory

	def set_default_scene(self, scene: Describer):
		if not self._isExported:
			if self._defaultScene != None:
				self._describersMap[C.GLTF_SCENE].remove(self._defaultScene)
			self._defaultScene = scene
			if not scene in self._describersMap[C.GLTF_SCENE]:
				self._describersMap[C.GLTF_SCENE].append(scene)
		else:
			print("Attempted to change default scene of already exported file.")

	def set_enforce_default_scene(self, enforce: bool):
		if not self._isExported:
			self._enforceDefaultScene = enforce
		else:
			print("Attempted to change scene enforcement of already exported file.")

	def get_enforce_default_scene(self) -> bool:
		return self._enforceDefaultScene
	
	def set_catch_stray_nodes(self, catchStrays: bool):
		if not self._isExported:
			self._catchStrayNodes = catchStrays
		else:
			print("Attempted to change stray catching of already exported file.")

	def get_catch_stray_nodes(self) -> bool:
		return self._catchStrayNodes

	def get_default_scene(self) -> Describer:
		return self._defaultScene

	def set_is_binary(self, binary: bool):
		if not self._isExported:
			self._isBinary = binary
		else:
			print("Attempted to change file type of already exported file.")
	
	def get_is_binary(self) -> bool:
		return self._isBinary

	def add_describers(self, describers: Describer | list[Describer]):
		if not self._isExported:
			if not type(describers) is list and not type(describers) is tuple:
				describers = [describers]

			for describer in describers:
				if describer._dataTypeHint in self._describersMap:
					self._describersMap[describer._dataTypeHint].append(describer)
		else:
			print(f"Attempted to add describer {describers} to already exported file")

	def __construct_gltf_dict(self) -> dict:
		items = [
			(C.GLTF_ASSET, {"generator": "Blender ggltf", "version": "2.0"}),
			(C.GLTF_EXTENSIONS_USED, []),
			(C.GLTF_EXTENSIONS_REQUIRED, []),
			(C.GLTF_SCENE, []),
			(C.GLTF_NODE, []),
			(C.GLTF_CAMERA, []),
			(C.GLTF_SKIN, []),
			(C.GLTF_ANIMATION, []),
			(C.GLTF_MESH, []),
			(C.GLTF_MATERIAL, []),
			(C.GLTF_TEXTURE, []),
			(C.GLTF_IMAGE, []),
			(C.GLTF_SAMPLER, []),
			(C.GLTF_EXTENSION, []),
			(C.GLTF_EXTRA, []),
			(C.GLTF_ACCESSOR, []),
			(C.GLTF_BUFFER_VIEW, []),
			(C.GLTF_BUFFER, [])
		]

		if self._enforceDefaultScene or self._defaultScene != None:
			items.insert(3, (C.GLTF_DEFAULT_SCENE, 0))

		return dict(items)
	
	def __enforce_default_scene(self, gltfDict: dict, topNodeIDs: list[int]):
		if len(gltfDict[C.GLTF_SCENE]) == 0:
			if len(topNodeIDs) > 0:
				scene = {
					C.SCENE_NAME : "Scene",
					C.SCENE_NODES : topNodeIDs
				}
				gltfDict[C.GLTF_DEFAULT_SCENE] = len(gltfDict[C.GLTF_SCENE])
				gltfDict[C.GLTF_SCENE].append(scene)


	def __find_top_nodes(self, gltfDict: dict) -> list:
		nodes = gltfDict[C.GLTF_NODE]
		isTopNode = [True] * len(nodes)
		topNodeIDs = []

		for n in nodes:
			if C.NODE_CHILDREN in n:
				for c in n[C.NODE_CHILDREN]:
					isTopNode[c] = False

		for i in range(0, len(isTopNode)):
			if isTopNode[i]:
				topNodeIDs.append(i)
		
		return topNodeIDs
	
	def __catch_stray_nodes(self, gltfDict: dict, topNodeIDs: list[int]):

		scenes = gltfDict[C.GLTF_SCENE]
		if len(scenes) == 0:
			return

		nodes = gltfDict[C.GLTF_NODE]
		isTopNode = [False] * len(nodes)
		isStrayNode = [True] * len(nodes)

		strayIDs = []

		for topNodeID in topNodeIDs:
			isTopNode[topNodeID] = True

		for s in scenes:
			if C.SCENE_NODES in s:
				for n in s[C.SCENE_NODES]:
					isStrayNode[n] = False

		for i in range(0, len(nodes)):
			if isTopNode and isStrayNode:
				strayIDs.append(i)

		defaultScene = gltfDict[C.GLTF_SCENE][gltfDict.get(C.GLTF_DEFAULT_SCENE, 0)]

		for strayID in strayIDs:
			if strayID in defaultScene[C.SCENE_NODES]:
				continue
			else:
				defaultScene[C.SCENE_NODES].append(strayID)


	def __export_as_gltf(self, where: str, gltfDict: dict):
		Util.prep_path(where)
		Util.cleanup_keys(gltfDict)

		f = open(where + C.FILE_EXT_GLTF, "w")
		jsonStr = json.dumps(gltfDict, indent="\t", ensure_ascii=False, separators=self._jsonSeparator)
		jsonStr = re.sub('(?<=[a-z"0-9-]),\n\t*', ",", jsonStr)
		jsonStr = re.sub('[[]\n\t*(?=[a-z0-9-])', "[", jsonStr)
		jsonStr = re.sub('(?<=[a-z"0-9-])\n\t*', "", jsonStr)
		jsonStr = re.sub('":[[]\n\t*(?=[a-z"0-9-])', '":[', jsonStr)
		jsonStr = re.sub('(?<=[a-z"0-9-])],\n\t*', "],", jsonStr)
		jsonStr = re.sub('(?<=\t){\n\t*', "{", jsonStr)
		jsonStr = re.sub('(?<=[]}])\n\t*}', "}", jsonStr) # there is probably a way to condense it into 1 line
		f.write(jsonStr)
		f.close()

	def __export_as_glb(self, where: str, gltfDict: dict):

		glbInternal = gltfDict.pop(C.GLB_TEMP_INTERNAL_BUFFER, None)

		Util.prep_path(where)
		Util.cleanup_keys(gltfDict)

		js = bytes(json.dumps(gltfDict, ensure_ascii=False, separators=self._jsonSeparator).encode("utf-8"))
		js_len = len(js) + len(js) % 4

		f = open(where + C.FILE_EXT_GLB, "w+b")

		f.write(struct.pack(C.PACKING_FORMAT_U_INT, C.FILE_BIN_MAGIC_NUMBER))
		f.write(struct.pack(C.PACKING_FORMAT_U_INT, C.FILE_BIN_VERSION_NUMBER))
		f.write(struct.pack(C.PACKING_FORMAT_U_INT, 0)) # temporarily write empty bytes where the file size should be
		f.write(struct.pack(C.PACKING_FORMAT_U_INT, js_len))
		f.write(struct.pack(C.PACKING_FORMAT_U_INT, C.FILE_BIN_CHUNK_TYPE_JSON))
		f.write(js)
		f.write(C.FILE_BIN_JSON_PAD * (len(js) % 4))

		if glbInternal != None:
			f.write(struct.pack(C.PACKING_FORMAT_U_INT, len(glbInternal) + len(glbInternal) % 4))
			f.write(struct.pack(C.PACKING_FORMAT_U_INT, C.FILE_BIN_CHUNK_TYPE_BIN))
			f.write(glbInternal)
			f.write(C.FILE_BIN_PAD * (len(glbInternal) % 4))
		
		# use current cursor position to determine the file size
		fileLength = f.tell()

		f.seek(8) # seek to where the file length is supposed to be
		f.write(struct.pack(C.PACKING_FORMAT_U_INT, fileLength)) # overwrite the temporary size of 0 to real size

		f.close()


	def get_referenced_describers(self):
		queue = []

		for describers in self._describersMap.values():
			queue += describers

		return queue

	def export_file(self) -> bool:
		absFilePath = os.path.abspath(bpy.path.abspath(self._fileDirectory))

		if absFilePath[-1] != os.path.sep:
			absFilePath = absFilePath + os.path.sep

		return self._export(self._isBinary, self.__construct_gltf_dict(), absFilePath + self._name)
	
	def _export(self, isBinary, gltfDict, fileTargetPath):
		def recursive_export(describer: Describer) -> bool:
			referencedDescribers = describer.get_referenced_describers()

			for referencedDescriber in referencedDescribers:
				if not referencedDescriber._isExported:
					if not recursive_export(referencedDescriber):
						return False
				
			if not describer._isExported:
				if not describer._export(isBinary, gltfDict, fileTargetPath):
					print(f"Describer: {describer} failed to export.")
					return False
				
			gltfDict[describer._dataTypeHint][describer._get_id_reservation(gltfDict)] = describer._exportedData
			return True

		if not self._isExported:
			exportQueue = self.get_referenced_describers()

			for desc in exportQueue:
				if not recursive_export(desc):
					print(f"Recursive export failed on: {desc}")
					self._isExported = True
					return False
				
			topNodes = self.__find_top_nodes(gltfDict)

			if self._defaultScene != None:
				gltfDict[C.GLTF_DEFAULT_SCENE] = self._defaultScene._get_id_reservation()
			else:
				if self._enforceDefaultScene:
					self.__enforce_default_scene(gltfDict, topNodes)

			if isBinary:
				self.__export_as_glb(fileTargetPath, gltfDict)
			else:
				self.__export_as_gltf(fileTargetPath, gltfDict)

			return True
		else:
			print("Attempted to export already export file.")
			return False