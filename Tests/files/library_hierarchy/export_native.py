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
    from io_advanced_gltf2.Advanced import Node
    from io_advanced_gltf2.Advanced import File

    from io_advanced_gltf2.Keywords import FILE_TYPE_GLTF_EMBEDDED, FILE_TYPE_GLB, FILE_TYPE_GLTF

    filePath = "//..\\..\\output\\"
    fileName = "library_hierarchy_export_native"
    binPath = ""


    def test(bucket):
        lib = "//..\..\lib_files\hierarchy.blend"
        Node.based_on_object(bucket, "0-0")
        File.dump_bucket(bucket)

    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))