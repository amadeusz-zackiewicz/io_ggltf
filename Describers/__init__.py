from .Base import ObjectBasedDescriber, Describer
from .Buffer import BufferDescriber
from .BufferView import BufferViewDescriber
from .Accessor import AccessorDescriber
from .Node import NodeDescriber
from .Mesh import MeshDescriber
from .Skin import SkinDescriber
from .Animation import AnimationDescriber
from .Scene import Scene
from .File import File


def MeshFromObject(objectName: str = None, objectLibrary: str = None, buffer: BufferDescriber = None) -> MeshDescriber:
	describer = MeshDescriber(buffer)
	describer.set_target(objName=objectName, objLibrary=objectLibrary)
	if describer._hasValidObject:
		return describer
	else:
		if objectLibrary != None:
			print(f"Failed to find target: {objectLibrary}::{objectName}")
		else:
			print(f"Failed to find target: {objectName}")
		return None
	
def NodeFromObject(objectName: str = None, objectLibrary: str = None, boneName: str = None, buffer: BufferDescriber = None) -> NodeDescriber:
	from io_ggltf.Core import BlenderUtil
	describer = NodeDescriber()
	describer.set_target(objName=objectName, objLibrary=objectLibrary, boneName=boneName)
	if describer._hasValidObject:
		if buffer != None:
			obj = Util.try_get_object((objectName, objectLibrary))
			if BlenderUtil.object_is_meshlike(obj):
				mesh = MeshDescriber(buffer)
				mesh.set_target(objectName, objectLibrary)
				mesh._floatPrecision = describer._floatPrecision
				describer._mesh = mesh
			if BlenderUtil.object_is_armature(obj):
				skin = SkinDescriber(buffer)
				skin.set_target(objectName, objectLibrary)
				skin._floatPrecision = describer._floatPrecision
				describer._skin = skin
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
	
def GltfFile(fileDirectory: str, fileName: str, binary: bool = True) -> File:
	return File(fileDirectory, fileName, binary)
