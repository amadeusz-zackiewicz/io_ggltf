# when a script is run in blender it is considered to be __main__ but
# when we run this as a file using terminal there is only 1 argument and
# when blender launches a python file it has 2 arguments
# so if there is only 1 argument, we are running it as a standalone python file
# otherwise blender is running it
import sys
if __name__ == "__main__" and len(sys.argv) == 1:
	import os
	sys.path.append(os.path.abspath(""))
	import Tests.LimitedTestUtil as T
	T.run_test("production_character", "production_character", os.path.basename(__file__).replace(".py", ""))
else:
	from io_ggltf.Describers import *
	from io_ggltf.Constants import *

	filePath = "//..\\..\\output\\"
	fileName = "production_character_filtered"
	binPath = "production_character_filtered"

	def test(buffer, asGlb):
		extraMeshObjNames = ["LP_Hair", 
					   "LP_Eye_Whites", 
					   "LP_eyes", 
					   "LP_Face_features",
					   "LP_Belt",
					   "LP_Belt_tip",
					   "LP_Jacket",
					   "LP_Jacket_tear",
					   "LP_Armband",
					   "LP_Hand.L",
					   "LP_Hand.R",
					   "LP_Boots",
					   "LP_Teeth",
					   "LP_Tongue"
					   ]
		node = NodeFromObject("RIG-trashblazer_f_meta")
		skin = SkinDescriber(buffer).set_target("RIG-trashblazer_f_meta").set_bone_filter(("(^DEF-)|(^root$)", True)).set_bone_hierarchy_stitching(True)

		skin.add_reparents(RIGIFY_META_HUMAN_REPARENTS)

		# my fault when creating the file, but at least i can test this
		skin.add_reparent("DEF-thumb.R.001", "DEF-hand.R")
		skin.add_reparent("DEF-thumb.L.001", "DEF-hand.L")
		skin.add_reparent("DEF-finger_index.R.001", "DEF-hand.R")
		skin.add_reparent("DEF-finger_index.L.001", "DEF-hand.L")
		skin.add_reparent("DEF-finger_middle.R.001", "DEF-hand.R")
		skin.add_reparent("DEF-finger_middle.L.001", "DEF-hand.L")
		skin.add_reparent("DEF-finger_ring.R.001", "DEF-hand.R")
		skin.add_reparent("DEF-finger_ring.L.001", "DEF-hand.L")
		skin.add_reparent("DEF-finder_pinky.R.001", "DEF-hand.R") # typo in file
		skin.add_reparent("DEF-finder_pinky.L.001", "DEF-hand.L") # typo in file

		skin.add_reparent("DEF-PHYS-belt_tail.001", "DEF-spine")

		skin.add_reparent("DEF-PHYS-hair_bangs.R.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_bangs.L.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_bangs.R.004", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_bangs.L.004", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_M_ears.R.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_M_ears.L.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_back.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_back.R.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_back.L.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_back.R.003", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_back.L.003", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_side.R.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_side.L.001", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_side.R.003", "DEF-spine.005")
		skin.add_reparent("DEF-PHYS-hair_side.L.003", "DEF-spine.005")

		skin.add_reparent("DEF-PHYS-jacket_arm_tear.R.001", "DEF-upper_arm.R")
		skin.add_reparent("DEF-PHYS-jacket_arm_tear.R.003", "DEF-upper_arm.R")
		skin.add_reparent("DEF-PHYS-jacket_top.R", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-jacket_top.L", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-jacket_bottom.F.R", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-jacket_bottom.F.L", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-jacket_bottom.M.R", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-jacket_bottom.M.L", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-jacket_bottom.B", "DEF-spine.003")

		skin.add_reparent("DEF-PHYS-breast.R", "DEF-spine.003")
		skin.add_reparent("DEF-PHYS-breast.L", "DEF-spine.003")

		skin.add_reparent("DEF-weapon_pivot.R", "DEF-hand.R")
		skin.add_reparent("DEF-weapon_pivot.L", "DEF-hand.L")


		node.set_mesh(MeshFromObject("LP_Body", buffer=buffer).set_uv_maps(True).merge_meshes(extraMeshObjNames)).set_skin(skin)

		GltfFile(filePath, fileName, asGlb).add_describers([node, skin, buffer]).export_file()


	print("---------- Start gltf")
	test(BufferDescriber(binPath), False)
	print("---------- Start glb")
	test(BufferDescriber(), True)