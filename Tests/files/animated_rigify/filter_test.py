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
	T.run_test("animated_rigify", "animated_rigify", os.path.basename(__file__).replace(".py", ""))
else:
	from io_ggltf.Describers import *
	from io_ggltf.Constants import *

	filePath = "//..\\..\\output\\"
	fileName = "animated_rigify_filter_test"
	binPath = "animated_rigify_filter_test"

	def test(buffer, asGlb):
		file = GltfFile(filePath, fileName, asGlb)
		node = NodeFromObject("rigify_rig")
		skin = SkinDescriber(buffer)
		skin.set_target("rigify_rig")
		skin.set_bone_filter(("(^DEF-)|(^root$)", True))
		skin.set_bone_hierarchy_stitching(True)

		skin.add_reparents(RIGIFY_META_HUMAN_REPARENTS)

		node._skin = skin

		file.add_describers([node, skin, buffer])
		
		file.export_file()


	print("---------- Start gltf")
	test(BufferDescriber(binPath), False)
	print("---------- Start glb")
	test(BufferDescriber(), True)