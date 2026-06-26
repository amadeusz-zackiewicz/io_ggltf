from .ExtensionObserver import ExtensionObserver
from .KHR_node_visibility import KHRNodeVisibility
from .KHR_animation_pointer import KHRAnimationPointers
from .GGLTF_node_extra_properties import NodeBoolean as NodeBooleanProperty
from .GODOT_single_root import GodotSingleRoot

def ext_godot_single_root(file):
	return GodotSingleRoot(file, file)

def ext_animation_pointers(file, animation):
	return KHRAnimationPointers(file, animation, kwargs={})

def ext_node_visibility(file, node, enableAnimation: bool = True):
	return KHRNodeVisibility(file, node, enableAnimation, kwargs={})

def ext_node_boolean_property(file, node, objProperty: str, exportName: str, enableAnimation: bool = True, addVariableMetaData: bool = False):
	return NodeBooleanProperty(file, node, objProperty, exportName, addVariableMetaData, enableAnimation)