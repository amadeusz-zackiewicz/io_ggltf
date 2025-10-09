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
	T.run_test("multi_mesh_merge", "multi_mesh_merge", os.path.basename(__file__).replace(".py", ""))
else:
	from io_ggltf.Describers import *
	from io_ggltf.Constants import *

	filePath = "//..\\..\\output\\"
	fileName = "multi_mesh_merge_test_merge"
	binPath = "multi_mesh_merge_test_merge"

	def test(buffer, asGlb):

		rotorNode = NodeFromObject("Rotor").set_mesh(MeshFromObject("Rotor", buffer=buffer))
		rearRotorNode = NodeFromObject("Rear_Rotor").set_mesh(MeshFromObject("Rear_Rotor", buffer=buffer))

		bodyMesh = MeshFromObject("Body", buffer=buffer).merge_meshes(["Landing_Gear", "Tail"]).set_origin_override("Helicopter")
		
		helicopterNode = NodeFromObject("Helicopter").set_mesh(bodyMesh).append_children([rotorNode, rearRotorNode])

		GltfFile(filePath, fileName, asGlb).add_describers([helicopterNode, buffer]).export_file()


	print("---------- Start gltf")
	test(BufferDescriber(binPath), False)
	print("---------- Start glb")
	test(BufferDescriber(), True)