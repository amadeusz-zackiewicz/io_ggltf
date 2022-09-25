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
    from io_ggltf.Advanced import *
    from io_ggltf.Keywords import *

    filePath = "//..\\..\\output\\"
    fileName = "multi_mesh_merge_check_autolink"
    binPath = ""

    def test(bucket):
        Settings.set_setting(bucket, BUCKET_SETTING_MESH_AUTO_LINK, True)

        Node.based_on_object(bucket, "Helicopter", parent=False)
        Node.based_on_object(bucket, "Rotor", parent=True)
        Node.based_on_object(bucket, "Rear_Rotor", parent=True)

        Mesh.merged_based_on_hierarchy(bucket, "Helicopter", name="helicopter_mesh", blacklist={"Rear_Rotor", "Rotor"})
        Mesh.based_on_object(bucket, "Rotor")
        Mesh.based_on_object(bucket, "Rear_Rotor")
        
        File.dump_bucket(bucket)

    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))