from .ExtensionObserver import ExtensionObserver
from .KHR_node_visibility import KHRNodeVisibility
from .KHR_animation_pointer import KHRAnimationPointers
from .GGLTF_node_extra_properties import NodeBoolean as NodeBooleanProperty
from .GODOT_single_root import GodotSingleRoot

def add_godot_single_root(file):
	return GodotSingleRoot(file, file)

def add_animation_pointers(file, animation):
	return KHRAnimationPointers(file, animation, kwargs={})

def add_node_visibility(file, node, enableAnimation: bool = True):
	return KHRNodeVisibility(file, node, enableAnimation, kwargs={})

def add_node_property_boolean(file, node, objProperty: str, exportName: str, enableAnimation: bool = True, addVariableMetaData: bool = False):
	return NodeBooleanProperty(file, node, objProperty, exportName, addVariableMetaData, enableAnimation)