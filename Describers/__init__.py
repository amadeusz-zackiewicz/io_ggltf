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
from io_ggltf.Core import ShowFunction


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
	
def NodeFromObject(
		objectName: str = None, 
		objectLibrary: str = None, 
		boneName: str = None, 
		boneFilter: tuple[str, bool] = None,
		includeMesh: bool = True, 
		includeSkin: bool = True, 
		includeCamera: bool = True, 
		buffer: BufferDescriber = None) -> NodeDescriber:
	from io_ggltf.Core import BlenderUtil, Util
	describer = NodeDescriber()
	describer.set_target(objName=objectName, objLibrary=objectLibrary, boneName=boneName)
	if describer._hasValidObject:
		if buffer != None:
			obj = Util.try_get_object((objectName, objectLibrary))
			if includeMesh and BlenderUtil.object_is_meshlike(obj):
				mesh = MeshDescriber(buffer)
				mesh.set_target(objectName, objectLibrary)
				mesh._floatPrecision = describer._floatPrecision
				describer._mesh = mesh
			elif includeSkin and BlenderUtil.object_is_armature(obj):
				skin = SkinDescriber(buffer)
				skin.set_bone_filter(boneFilter)
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
	
def NodeHierarchy(
		topObjectName: str, 
		topObjectLibrary: str = None, 
		objectFilter: tuple[str, bool] = None, 
		boneFilter: tuple[str, bool] = None, 
		includeMeshes: bool = True, 
		includeSkins: bool = True, 
		includeCameras: bool = True,
		buffer: BufferDescriber = None
		) -> NodeDescriber:
	from io_ggltf.Core import BlenderUtil, Util
	from io_ggltf import Constants as C

	def recusrive(obj, parentDescriber: NodeDescriber):
		for child in obj.children:
			if objectFilter != None:
				if not Util.name_passes_filter(objectFilter, child.name):
					continue

			childDesc = NodeFromObject(child.name, child.library, None, boneFilter=boneFilter, includeMesh=includeMeshes, includeSkin=includeSkins, includeCamera=includeCameras, buffer=buffer)
			
			if child.parent_type == C.BLENDER_TYPE_OBJECT:
				parentDescriber.append_child(childDesc)
			elif child.parent_type == C.BLENDER_TYPE_BONE:
				if parentDescriber._skin != None:
					parentDescriber._skin.lock_bone_hierarchy()
					if child.parent_bone in parentDescriber._skin._skinDefinition:
						boneDesc = parentDescriber._skin._boneNodeDescribers[parentDescriber._skin._skinDefinition[child.parent_bone]]
						boneDesc.append_child(childDesc)
					else:
						continue
				else:
					parentDescriber.append_child(childDesc)
			else:
				parentDescriber.append_child(childDesc)

			recusrive(child, childDesc)

	topDescriber = NodeFromObject(topObjectName, topObjectLibrary, None, boneFilter=boneFilter, includeMesh=includeMeshes, includeSkin=includeSkins, includeCamera=includeCameras, buffer=buffer)
	
	if not topDescriber._hasValidObject:
		print(f"Failed to find object: {topObjectName}" if topObjectLibrary == None else f"Failed to find object: {topObjectLibrary}::{topObjectName}")
		return None
	
	recusrive(Util.try_get_object((topObjectName, topObjectLibrary)), topDescriber)

	return topDescriber
	
def BufferInternal() -> BufferDescriber:
	return BufferDescriber()

def BufferExternal(relative_path: str) -> BufferDescriber:
	return BufferDescriber(relative_path)
	
def GltfFile(fileDirectory: str, fileName: str, binary: bool = True) -> File:
	return File(fileDirectory, fileName, binary)


ShowFunction.Register(GltfFile, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/")
ShowFunction.Register(BufferInternal, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/")
ShowFunction.Register(BufferExternal, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/")
ShowFunction.Register(MeshFromObject, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/")
ShowFunction.Register(NodeFromObject, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/")
ShowFunction.Register(NodeHierarchy, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/")