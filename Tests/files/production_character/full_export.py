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
	fileName = "production_character_full_export"
	binPath = "production_character_full_export"

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
		file = GltfFile(filePath, fileName, asGlb)
		node = NodeFromObject("RIG-trashblazer_f_meta")
		skin = SkinDescriber(buffer)
		skin.set_target("RIG-trashblazer_f_meta")
		mesh = MeshFromObject("LP_Body", buffer=buffer)
		mesh.set_uv_maps(True)

		for extraMesh in extraMeshObjNames:
			mesh.merge_mesh(extraMesh)
		
		node._mesh = mesh
		mesh._skin = skin
		node._skin = skin

		file.add_describers([node, mesh, skin, buffer])
		
		file.export_file()


	print("---------- Start gltf")
	test(BufferDescriber(binPath), False)
	print("---------- Start glb")
	test(BufferDescriber(), True)