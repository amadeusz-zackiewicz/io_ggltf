from collections import OrderedDict
from io_ggltf import Constants as C
from io_ggltf.Describers import *
from io_ggltf.Core import Util, BlenderUtil
from difflib import SequenceMatcher

class SkinDescriber(ObjectBasedDescriber):
	def __init__(self, buffer: BufferDescriber):
		super().__init__()

		self._dataTypeHint = C.GLTF_SKIN

		self._buffer = buffer

		self._rootBoneName: bool | str = False
		self._includeInverseBindMatrices: bool = True
		self._stitchHierarchy: bool = False
		self._boneFilter: tuple[str, bool] = None
		self._keepPose: bool = False
		self._floatPrecision: int = 7

		self._extraArmatureNames: list[str] = []
		self._extraArmatureLibraries: list[str] = []
		self._extraArmatureParentBoneName: list[str] = []

		self._boneNodeDescribers: list[NodeDescriber] = []
		self._topBoneDescribers: list[NodeDescriber] = []
		self._attachedObjDescribers: list[NodeDescriber] = []

		self._jointNodeIDs: list[int] = []
		self._topJointNodeIds: list[int] = []

		self._jointTree: list[Joint] = []
		self._joints: dict[str, Joint] = {}
		self._skinDefinition: OrderedDict[str, int] = {}

		self._hierarchyLocked: bool = False
		self._reparentDict: dict[str, str] = {}

	def get_referenced_describers(self):
		return set(self._boneNodeDescribers)

	def set_target(self, objName, objLibrary = None):
		if not self._isExported and not self._hierarchyLocked:
			if BlenderUtil.object_is_armature(Util.try_get_object((objName, objLibrary))):
				super().set_target(objName, objLibrary)
			else:
				print(f"Tried to set object that is not of type: '{C.BLENDER_TYPE_ARMATURE}' on skin describer.")
		else:
			print(f"Tried to change target object on skin that is already locked in or exported.")

	def append_extra_armatures(self, objName: str, objLibrary: str = None, parentBoneName: str = None):
		if not self._isExported and not self._hierarchyLocked:
			if BlenderUtil.object_is_armature(Util.try_get_object((objName, objLibrary))):
				self._extraArmatureNames.append(objName)
				self._extraArmatureLibraries.append(objLibrary)
				self._extraArmatureParentBone.append(parentBoneName)
			else:
				print(f"Tried to append extra armature object that is not of type: {C.BLENDER_TYPE_ARMATURE} on skin describer.")
		else:
			print(f"Tried to append extra armatures on skin that is already locked in or exported.")

	def set_bone_filter(self, filter: tuple[str, bool]):
		if not self._isExported and not self._hierarchyLocked:
			self._boneFilter = filter
		else:
			print(f"Tried to set bone filter on skin that is already locked in or exported.")

	def set_bone_hierarchy_stitching(self, stitch: bool):
		if not self._isExported and not self._hierarchyLocked:
			self._stitchHierarchy = stitch
		else:
			print(f"Tried to set hierarchy stitching on skin that is already locked in or exported.")

	def set_root(self, rootBoneName: bool | str):
		if not self._isExported and not self._hierarchyLocked:
			self._rootBoneName = rootBoneName
		else:
			print(f"Tried to set root bone on skin that is already locked in or exported.")

	def set_include_inverse_binds(self, includeIB: bool):
		if not self._isExported:
			self._includeInverseBindMatrices = includeIB
		else:
			print(f"Tried to set inverse binds inclusion on already exported skin.")

	def set_keep_pose(self, keepPose: bool):
		if not self._isExported and not self._hierarchyLocked:
			self._keepPose = keepPose
		else:
			print(f"Tried to change keep pose on skin that is already locked in or exported.")

	def add_reparent(self, childName: str, parentName: str):
		if not self._isExported and not self._hierarchyLocked:
			self._reparentDict[childName] = parentName
		else:
			print(f"Tried to add reparent to skin that is already locked in or exported.")

	def add_reparents(self, reparents: dict[str, str]):
		if not self._isExported and not self._hierarchyLocked:
			self._reparentDict =  self._reparentDict | reparents
		else:
			print(f"Tried to add reparent to skin that is already locked in or exported.")

	def __determine_root_bone(self, armatureObj) -> str: # find first unparented bone
		for bone in armatureObj.pose.bones:
			if bone.parent == None:
				return bone.name
		return None
	
	def __create_joints_recursive(self, bone, obj, joints: dict):
		includeThisBone = False

		if self._boneFilter != None:
			if Util.name_passes_filter(self._boneFilter, bone.name):
				includeThisBone = True
		else:
			includeThisBone = True

		if not includeThisBone and not self._stitchHierarchy:
			return None
		elif includeThisBone:
			joint = Joint(bone, obj)
			joints[bone.name] = joint

		if self._stitchHierarchy:
			for c in bone.children:# scan all bones and create joint for each
				self.__create_joints_recursive(c, obj, joints) 
		else: # normal filter only
			if self._boneFilter == None:
				for c in bone.children:
					child = self.__create_joints_recursive(c, obj, joints)
					child.parentJoint = joint
					joint.childrenJoints.append(child)
			else:
				for c in bone.children:
					if Util.name_passes_filter(self._boneFilter, c.name):
						child = self.__create_joints_recursive(c, obj, joints)
						child.parentJoint = joint
						joint.childrenJoints.append(child)
		
		return joint if includeThisBone else None
	
	def __convert_joint_into_nodes_recursive(self, joint, mainArmatureObj, parentJoint = None) -> NodeDescriber:
		node = NodeDescriber()
		joint.nodeDescriber = node
		
		node.set_target(joint.armatureObj.name, joint.armatureObj.library, joint.bone.name)

		for c in joint.childrenJoints:
			node.append_child(self.__convert_joint_into_nodes_recursive(c, mainArmatureObj, joint))
		
		return node
	
	def __export_nodes(self, isBinary, gltfDict, fileTargetPath):
		def recursive(node: NodeDescriber):
			if not node._isExported:
				node._export(isBinary, gltfDict, fileTargetPath)
			for c in node._children:
				recursive(c)

		for joint in self._jointTree:
			recursive(joint.nodeDescriber)
			self._topJointNodeIds.append(joint.nodeDescriber._get_id_reservation(gltfDict))
	
	def __set_joint_nodes_transforms(self):
		def recursive(joint):
			parentJoint = joint.parentJoint
			if parentJoint == None:
				translation, rotation, scale = Util.get_yup_transforms(
					(joint.armatureObj.name, joint.armatureObj.library, joint.bone.name),
					(mainArmatureObj.name, mainArmatureObj.library))
			else:
				translation, rotation, scale = Util.get_yup_transforms(
					(joint.armatureObj.name, joint.armatureObj.library, joint.bone.name),
					(parentJoint.armatureObj.name, parentJoint.armatureObj.library, parentJoint.bone.name))
				
			joint.nodeDescriber._translation = Util.bl_math_to_gltf_list(translation)
			joint.nodeDescriber._rotation = Util.bl_math_to_gltf_list(rotation)
			joint.nodeDescriber._scale = Util.bl_math_to_gltf_list(scale)

			for cJoint in joint.childrenJoints:
				recursive(cJoint)

		mainArmatureObj = Util.try_get_object((self._objectName, self._objectLibrary))

		for joint in self._jointTree:
			recursive(joint)

	def __export_inverse_binds(self, mainObjectWorldMatrix, isBinary, gltfDict, fileTargetPath):
		if not self._includeInverseBindMatrices:
			return

		inverseBinds = [None] * len(self._joints)

		for iJoint, joint in enumerate(self._joints.values()):
			inverseBinds[iJoint] = Util.y_up_matrix(mainObjectWorldMatrix.inverted_safe() @ joint.worldMatrix.inverted_safe())
			inverseBinds[iJoint].transpose()

		accessor = AccessorDescriber()
		accessor.set_float_precision(self._floatPrecision)
		accessor.insert_data(inverseBinds, 
					   self._buffer, 
					   C.ACCESSOR_TYPE_MATRIX_4,
					   C.ACCESSOR_COMPONENT_TYPE_FLOAT,
					   C.PACKING_FORMAT_FLOAT
					   )
		
		accessor._export(isBinary, gltfDict, fileTargetPath)
		gltfDict[C.GLTF_ACCESSOR][accessor._get_id_reservation(gltfDict)] = accessor._exportedData
		gltfDict[C.GLTF_BUFFER_VIEW][accessor._bufferView._get_id_reservation(gltfDict)] = accessor._bufferView._exportedData
		
		self._exportedData[C.SKIN_INVERSE_BIND_MATRICES] = accessor._get_id_reservation(gltfDict)

	def __build_hierarchy(self):
		if self._hierarchyLocked:
			return
		
		armatureObjects: list = [Util.try_get_object((self._objectName, self._objectLibrary))]

		if type(self._rootBoneName) == str:
			mainRootBone = Util.try_get_bone((self._objectName, self._objectLibrary, self._rootBoneName))
		else:
			mainRootBone = self.__determine_root_bone(armatureObjects[0])

		parentBoneName: list[str] = [mainRootBone]

		for i, _ in enumerate(self._extraArmatureNames):
			armatureObjects.append(Util.try_get_object(self._extraArmatureNames[i], self._extraArmatureLibraries[i]))
			if self._extraArmatureParentBone[i] != None:
				parentBoneName.append(self._extraArmatureParentBone[i])
			else:
				parentBoneName.append(mainRootBone)

			parentBoneName.insert(0, mainRootBone)

		jointParentFallbacks: list[str] = []

		for iArmature, armatureObj in enumerate(armatureObjects):
			rootBones = []

			if self._boneFilter == None:
				for bone in armatureObj.pose.bones:
					if bone.parent == None:
						rootBones.append(bone)
			elif self._stitchHierarchy:
				for bone in armatureObj.pose.bones:
					if bone.parent == None or not Util.name_passes_filter(self._boneFilter, bone.parent.name):
						rootBones.append(bone)
			else:
				for bone in armatureObj.pose.bones:
					if bone.parent == None:
						if not Util.name_passes_filter(self._boneFilter, bone.name):
							continue
						else:
							rootBones.append(bone)
			

			jointsLen: int = len(self._joints)
			for rootBone in rootBones:
				joint = self.__create_joints_recursive(rootBone, armatureObj, self._joints)
			jointParentFallbacks += [parentBoneName[iArmature]] * int(len(self._joints) - jointsLen)

		if self._stitchHierarchy:
			for iJoint, joint in enumerate(self._joints.values()):
				if joint.parentJoint == None:
					jointParent = joint.try_get_stitched_parent(self._boneFilter, self._joints)
					if jointParent == None:
						if joint.bone.name != jointParentFallbacks[iJoint]:
							jointParent = self._joints.get(jointParentFallbacks[iJoint], None)

					if jointParent != None:
						joint.parentJoint = jointParent
						jointParent.childrenJoints.append(joint)
						
		print(self._reparentDict)
		for reparentChildJointName, reparentParentJointName in self._reparentDict.items():
			childJoint: Joint = self._joints.get(reparentChildJointName)
			parentJoint: Joint = self._joints.get(reparentParentJointName)

			if childJoint == None or parentJoint == None:
				continue

			childJoint.parentJoint.childrenJoints.remove(childJoint)
			childJoint.parentJoint = parentJoint
			parentJoint.childrenJoints.append(childJoint)

		for joint in self._joints.values():
			if joint.parentJoint == None:
				self._jointTree.append(joint)

		for iJoint, jointName in enumerate(self._joints.keys()):
				self._skinDefinition[jointName] = iJoint

		for rootJoint in self._jointTree:
			self._boneNodeDescribers.append(self.__convert_joint_into_nodes_recursive(rootJoint, armatureObjects[0]))

		self._hierarchyLocked = True

	def _export(self, isBinary, gltfDict, fileTargetPath):
		if not self._isExported:

			self.__build_hierarchy()

			armatureObjects: list = [Util.try_get_object((self._objectName, self._objectLibrary))]
			depsGraph = BlenderUtil.get_depsgraph()
			oldPoseMode: list = []

			if self._keepPose:
				for obj in armatureObjects:
					oldPoseMode.append(BlenderUtil.get_armature_pose_mode(obj))
					BlenderUtil.set_armature_pose_mode(obj, C.BLENDER_ARMATURE_POSE_MODE)
			else:
				for obj in armatureObjects:
					oldPoseMode.append(BlenderUtil.get_armature_pose_mode(obj))
					BlenderUtil.set_armature_pose_mode(obj, C.BLENDER_ARMATURE_REST_MODE)

			depsGraph.update()

			for rootJoint in self._jointTree:
				self._topJointNodeIds.append(rootJoint.nodeDescriber._get_id_reservation(gltfDict))

			self._jointNodeIDs = [None] * len(self._joints)
			for iJoint, joint in enumerate(self._joints.values()):
				joint.calculate_world_matrix()
				self._jointNodeIDs[iJoint] = joint.nodeDescriber._get_id_reservation(gltfDict)

			self.__set_joint_nodes_transforms()

			self._export_name()
			self.__export_inverse_binds(armatureObjects[0].matrix_world, isBinary, gltfDict, fileTargetPath)
			self.__export_nodes(isBinary, gltfDict, fileTargetPath)

			self._exportedData[C.SKIN_JOINTS] = self._jointNodeIDs

			if self._rootBoneName:
				skeletonID = self._joints.get(self._rootBoneName, None)
				if skeletonID != None:
					self._exportedData[C.SKIN_SKELETON] = skeletonID

			for joint in self._joints.values():
				if not joint.nodeDescriber._isExported:
					joint.nodeDescriber._export(isBinary, gltfDict, fileTargetPath)
					gltfDict[C.GLTF_NODE][joint.nodeDescriber._get_id_reservation(gltfDict)] = joint.nodeDescriber._exportedData

			for i, oldPoseMode in enumerate(oldPoseMode):
				BlenderUtil.set_armature_pose_mode(armatureObjects[i], oldPoseMode)

			depsGraph.update()
			
			self._insert_exported_data_to_dict(gltfDict)
			self._isExported = True
			return True
		else:
			print(f"Tried to export skin that is already exported.")
			return False

	
class Joint:
	def __init__(self, bone, armatureObj):
		self.bone = bone
		self.armatureObj = armatureObj
		self.parentJoint: Joint = None
		self.parentFallbackName: str = None
		self.worldMatrix = None
		self.childrenJoints: list[Joint] = []
		self.attachmentsNames: list[str] = []
		self.attachmentLibraries: list[str] = []

		self.nodeDescriber: NodeDescriber = None

	def calculate_world_matrix(self):
		self.worldMatrix = Util.y_up_matrix(self.armatureObj.matrix_world) @ self.bone.bone.matrix_local

	def try_get_stitched_parent(self, filter: tuple[str, bool], joints):
		parentList = self.bone.parent_recursive
		
		if filter != None:
			for parent in parentList:
				parentJoint = joints.get(parent.name, None)
				if parentJoint != None:
					return parentJoint
		else:
			if len(parentList) > 0:
				return joints.get(parentList[0].name, None)
			
		return None

