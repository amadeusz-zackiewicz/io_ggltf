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
    T.run_test("instanced_collection", "instanced_collection", os.path.basename(__file__).replace(".py", ""))
else:
    from io_advanced_gltf2.Advanced import *
    from io_advanced_gltf2.Keywords import *

    filePath = "//..\\..\\output\\"
    fileName = "instanced_collection_export_original"
    binPath = ""

    def test(bucket):
        Node.based_on_collection(bucket, "Original_collection")
        File.dump_bucket(bucket)

    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))