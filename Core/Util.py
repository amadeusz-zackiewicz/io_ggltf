from io_ggltf import Constants as __c
from io_ggltf.Core import BlenderUtil
import os
from mathutils import Matrix, Vector, Quaternion, Euler
from bpy_extras.io_utils import axis_conversion
import bpy
import re

class ObjectNotFoundException(Exception):
	def __init__(self, objAccessor):
		if type(objAccessor) == tuple:
			print(f"{objAccessor[1]}::{objAccessor[0]} not found within blend file, please check if the library path is correct and linked correctly")
		elif type(objAccessor) == str:
			print(f"{objAccessor} not found within blend file")
		else:
			print(f"Invalid format used while getting object, expected tuple(object name, library) or string, got: {objAccessor}")

class BoneNotFoundException(Exception):
	def __init__(self, accessor):
		self.accessor = accessor

	def __str__(self):
		return f"Bone '{self.accessor[2]}' not found in '{self.accessor[0]}'"

def y_up_matrix(orgMat : Matrix) -> Matrix:
	"""
	Multiply the matrix to make it Y+ up
	"""
	return get_basis_matrix_conversion() @ orgMat

def y_up_location(orgLoc : Vector) -> Vector:
	"""
	Move and flip individual components to match Y+ up coordinate system.
	"""
	return Vector((orgLoc[0], orgLoc[2], -orgLoc[1]))

def y_up_rotation(orgRot : Quaternion) -> Quaternion:
	"""
	Move and flip individual components to match Y+ up coordinate system.
	Warning: This does not swizzle the order from WXYZ to XYZW.
	"""
	return Quaternion((orgRot[0], orgRot[1], orgRot[3], -orgRot[2]))

def y_up_scale(orgScl : Vector) -> Vector:
	"""
	Move and flip indivual components to match Y+ up coordinate system
	"""
	return Vector((orgScl[0], orgScl[2], orgScl[1]))

def y_up_direction(orgDir: Vector) -> Vector:
	"""
	Move and flip individual components to match Y+ up coordinate system.
	"""
	return Vector((orgDir[0], orgDir[2], -orgDir[1]))

def correct_uv(orgUV: Vector) -> Vector:
	"""
	Move, flip and compensate for difference in V coordinates.
	"""
	return Vector((orgUV[0], -orgUV[1] + 1.0))

def bl_math_to_gltf_list(obj):
	"""
	Flatten the object into a list.
	For Quaternions: Swizzle the order from WXYZ to XYZW.
	"""
	if isinstance(obj, Quaternion):
		return [obj[1], obj[2], obj[3], obj[0]]
	elif isinstance(obj, Matrix):
		l = []
		rows = len(obj)
		cols = len(obj[0])
		for r in range(0, rows):
			for c in range(0, cols):
				l.append(obj[r][c])
		return l
	else:
		return list(obj)

def round_float_list_to_precision(data: list, precision: int):
	"""
	Round floats to specified decimal point.
	"""
	for i, f in enumerate(data):
		data[i] = round(f, precision)

def cleanup_keys(d: dict):
	to_pop = []
	for k in d.keys():
		#print(f"{k} is of type {type(d[k])}")
		value = d[k]
		if value == None:
			to_pop.append(k)
		elif type(value) == list or type(value) == tuple or type(value) == dict:
			if len(value) == 0:
				to_pop.append(k)
	for p in to_pop:
		d.pop(p)

def get_basis_matrix_conversion():
	convert = axis_conversion(from_forward="-Y", from_up="Z", to_forward="Z", to_up="Y")
	convert.resize_4x4()
	return convert

def try_get_object(accessor):
	try:
		if type(accessor) == str or (type(accessor) == tuple and len(accessor) == 2):
			obj = bpy.data.objects.get(accessor)
			if obj == None:
				raise ObjectNotFoundException(accessor)
			return obj
		else: # in case we get a bone accessor
			obj = bpy.data.objects.get((accessor[0], accessor[1])) # strip the bone name
			if obj == None:
				raise ObjectNotFoundException(accessor)
			return obj

	except Exception as e:
		print(e)
		return None

def try_get_bone(accessor):
	try:
		if type(accessor) == str or (type(accessor) == tuple and len(accessor) == 2):
			return None
		else:
			obj = bpy.data.objects.get((accessor[0], accessor[1]))
			if obj == None:
				return None
			bone = obj.pose.bones[accessor[2]]
			if bone == None:
				return None
			return bone

	except Exception as e:
		return None
	
def get_bone(obj, boneName):
	try:
		bone = obj.pose.bones[boneName]
		return bone
	
	except Exception as e:
		return None
	
def name_passes_filters(filter: list[tuple], name: str) -> bool:
	for f in filter:
		#print(f"Filter: {f[0]} | Name: {name} | Whitelist: {f[1]} | Match: {re.search(f[0], name)}")
		match = re.search(f[0], name)
		if f[1] == True: # if its a white list
			if match == None: # and we failed to find a match
				return False 
		else: # if its a blacklist
			if match != None: # and we found a match
				return False
	return True

def name_passes_filter(filter: tuple[str, bool], name:str) -> bool:
	match = re.search(filter[0], name)
	if filter[1] == True: # Whitelist
		if match == None: return False
		else: return True
	else: # Blacklist
		return match == None

def rename_node(bucket, nodeID: int, newName: str):
	node = bucket.data[__c.BUCKET_DATA_NODES][nodeID]
	node[__c.NODE_NAME] = newName

def rename_node(bucket, nodeName: str, newName: str):
	for n in bucket.data[__c.BUCKET_DATA_NODES]:
		if nodeName == n[__c.NODE_NAME]:
			n[__c.NODE_NAME] = newName

def pattern_replace(bucket, dataType: str, pattern: str, newStr: str):
	objects = bucket.data[dataType]
	pattern = re.compile(pattern)
	for obj in objects:
		if __c.__VAR_NAME in obj: # the object here is a dictionary so we check if it has a name first
			name = obj[__c.__VAR_NAME]
			matches = re.findall(pattern, name)
			uniqueMatches = set()
			if len(matches)> 0:
				if type(matches[0]) == tuple:
					for group in matches:
						for match in group:
							if match != "":
								uniqueMatches.add(match)
				else:
					for match in matches:
						uniqueMatches.add(match)

				for unique in uniqueMatches:
					name = name.replace(unique, newStr)
				obj[__c.__VAR_NAME] = name

def pattern_replace_node_name(bucket, nodeID, pattern: str, newStr: str):
	node = bucket.data[__c.BUCKET_DATA_NODES][nodeID]
	if __c.NODE_NAME in node:
		name = node[__c.NODE_NAME]
		matches = re.findall(pattern, name)
		uniqueMatches = set()
		if len(matches) > 0:
			if type(matches[0]) == tuple:
				for group in matches:
					for match in group:
						if match != "":
							uniqueMatches.add(match)
			else:
				for match in matches:
					uniqueMatches.add(match)

			
			for unique in uniqueMatches:
				name = name.replace(unique, newStr)
				
			node[__c.NODE_NAME] = name

def pattern_replace_skin_joint_names(bucket, skinID: int, pattern: str, newStr: str):
	skin = bucket.data[__c.BUCKET_DATA_SKINS][skinID]

	if __c.SKIN_JOINTS in skin:
		for joint in skin[__c.SKIN_JOINTS]:
			pattern_replace_node_name(bucket, joint, pattern, newStr)

def create_filter(pattern: str, whitelist: bool):
	return (pattern, whitelist)

def get_all_nodes_in_scene(bucket, sceneID) -> set[int]:
	if not __c.BUCKET_DATA_SCENES in bucket.data or not __c.BUCKET_DATA_NODES in bucket.data:
		return None
	
	nodes = set()
	scene = bucket.data[__c.BUCKET_DATA_SCENES][sceneID]

	if not __c.SCENE_NODES in scene:
		return None

	for nodeID in scene[__c.SCENE_NODES]:
		if nodeID in nodes:
			continue
		hierarchy = get_all_nodes_in_hierarchy(bucket, nodeID)
		nodes.update(hierarchy)
		
	return nodes

def get_all_nodes_in_hierarchy(bucket, topNodeID):
	def add_children(bucket, node: dict, nodes: set):
		if not __c.NODE_CHILDREN in node:
			return
		for c in node[__c.NODE_CHILDREN]:
			add_children(bucket, bucket.data[__c.BUCKET_DATA_NODES][c], nodes)
			nodes.add(c)

	nodes = set()
	node = bucket.data[__c.BUCKET_DATA_NODES][topNodeID]
	nodes.add(topNodeID)

	add_children(bucket, node, nodes)
	return nodes

def get_yup_transforms(childAccessor, parent):
	
	yUpMatrix = evaluate_matrix(childAccessor, parent)

	location, rotation, scale = yUpMatrix.decompose()
	location = y_up_location(location)
	rotation = y_up_rotation(rotation)
	scale = y_up_scale(scale)
	return (location, rotation, scale)

def evaluate_matrix(childAccessor, parent, depsgraph = None):
	if childAccessor == None:
		return Matrix()
	
	if depsgraph == None:
		depsgraph = BlenderUtil.get_depsgraph()

	if type(childAccessor) == str:
		childAccessor = (childAccessor, None)

	yUpMatrix = None

	childObj = depsgraph.id_eval_get(try_get_object(childAccessor))

	if len(childAccessor) == 3:
		childBone = get_bone(childObj, childAccessor[2])
		childWorldMatrix = childObj.matrix_world @ childBone.matrix
	else:
		childWorldMatrix = childObj.matrix_world


	if parent != None:
		if type(parent) == str:
			parent = (parent, None)

		parentObj = depsgraph.id_eval_get(try_get_object(parent))
		
		if len(parent) == 3:
			parentBone = get_bone(parentObj, parent[2])
			parentWorldMatrix = parentObj.matrix_world @ parentBone.matrix
		else:
			parentWorldMatrix = parentObj.matrix_world

		yUpMatrix = parentWorldMatrix.inverted_safe() @ childWorldMatrix
	else:
		yUpMatrix = childWorldMatrix

	return yUpMatrix

def get_world_matrix(accessor: tuple):
	depsgraph = BlenderUtil.get_depsgraph()
	obj = depsgraph.id_eval_get(try_get_object(accessor))

	if len(accessor) == 3:
		bone = try_get_bone(accessor)

	if bone != None:
		return obj.matrix_world @ bone.matrix
	else:
		return obj.matrix_world
	
def prep_path(path : str):
	os.makedirs(os.path.dirname(path), exist_ok=True)