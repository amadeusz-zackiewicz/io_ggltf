from io_ggltf import Constants as C
from io_ggltf.Describers import *

class Scene(Describer):
	def __init__(self):
		super().__init__()

		self._dataTypeHint = C.GLTF_SCENE

		self._nodes: list[NodeDescriber]

	def append_node(self, node: NodeDescriber):
		if not self._isExported:
			self._nodes.append(node)
		else:
			print("Attempted to append a node to scene that is already exported.")

	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:
			self._export_name()

			if len(self._nodes) > 0:
				nodeIDs = []

				for node in self._nodes:
					nodeIDs.append(node._get_id_reservation())

				self._exportedData[C.SCENE_NODES] = nodeIDs

		else:
			print("Attempted to export a scene that is already exported.")