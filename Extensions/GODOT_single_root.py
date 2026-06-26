from io_ggltf import Constants as C
from io_ggltf.Describers import File as GltfDescriber
from io_ggltf.Extensions import ExtensionObserver

# https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Vendor/GODOT_single_root
class GodotSingleRoot(ExtensionObserver):
	def __init__(self, file, target, **kwargs):
		super().__init__("GODOT_single_root", file, target, kwargs=kwargs)
		self.__allowAnimation = False
		self._enableAnimation = False
