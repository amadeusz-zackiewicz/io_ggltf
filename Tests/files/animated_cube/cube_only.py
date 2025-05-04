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
	T.run_test("animated_cube", "animated_cube", os.path.basename(__file__).replace(".py", ""))
else:
	from io_ggltf.Describers import *
	from io_ggltf.Constants import *

	filePath = "//..\\..\\output\\"
	fileName = "animated_cube_cube_only"
	binPath = "animated_cube_cube_only"

	def test(buffer, asGlb):
		file = GltfFile(filePath, fileName, asGlb)
		node = NodeFromObject("Cube")
		node._mesh = MeshFromObject("Cube", buffer=buffer)
		file.add_describers([node, buffer])
		
		file.export_file()


	print("---------- Start gltf")
	test(Buffer(binPath), False)
	print("---------- Start glb")
	test(Buffer(), True)