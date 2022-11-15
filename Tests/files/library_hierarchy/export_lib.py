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
    T.run_test("library_hierarchy", "library_hierarchy", os.path.basename(__file__).replace(".py", ""))
else:
    from io_ggltf.Advanced import *
    from io_ggltf.Constants import *

    filePath = "//..\\..\\output\\"
    fileName = "library_hierarchy_export_lib"
    binPath = ""


    def test(bucket):
        lib = "//..\..\lib_files\hierarchy.blend"
        Node.based_on_hierarchy(bucket, ("0-0", lib))
        File.dump_bucket(bucket)

    print("---------- Start gltf embedded")
    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    print("---------- Start gltf with external binaries")
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    print("---------- Start glb")
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))