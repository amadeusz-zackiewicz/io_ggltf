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
    T.run_test("multi_armature_mesh", "multi_armature_mesh", os.path.basename(__file__).replace(".py", ""))
else:
    from io_advanced_gltf2.Advanced import Skin
    from io_advanced_gltf2.Advanced import File

    from io_advanced_gltf2.Keywords import FILE_TYPE_GLTF_EMBEDDED, FILE_TYPE_GLB, FILE_TYPE_GLTF

    filePath = "//..\\..\\output\\"
    fileName = "multi_armature_mesh_export_both"
    binPath = ""

    def test(bucket):
        Skin.based_on_object_modifiers(bucket, "MeshObj", getInverseBinds=True, forceRestPose=True)
        File.dump_bucket(bucket)

    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))