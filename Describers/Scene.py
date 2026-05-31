from io_ggltf import Constants as C
from io_ggltf.Describers import *

class Scene(Describer):
	def __init__(self):
		super().__init__()

		self._dataTypeHint = C.GLTF_SCENE

		self._nodes: list[NodeDescriber] = []

	def append_node(self, node: NodeDescriber):
		if not self._isExported:
			self._nodes.append(node)
		else:
			print("Attempted to append a node to scene that is already exported.")
		return self
	
	def append_nodes(self, nodes: list[NodeDescriber]):
		if not self._isExported:
			for node in nodes:
				self.append_node(node)
		else:
			print("Attempted to append a node to scene that is already exported.")
		return self
	
	def get_referenced_describers(self) -> set:
		unique_nodes = set()
		for node in self._nodes:
			unique_nodes.add(node)
		return unique_nodes

	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			self._export_name()

			if len(self._nodes) > 0:
				nodeIDs = []

				for node in self._nodes:
					hierarchy: list[NodeDescriber] = node.get_flattened_hierarchy()
					for offspring in hierarchy:
						if offspring.get_parent() == None:
							nodeIDs.append(offspring._get_id_reservation(gltfDict))

				self._exportedData[C.SCENE_NODES] = nodeIDs
			return True
		else:
			print("Attempted to export a scene that is already exported.")
			return False