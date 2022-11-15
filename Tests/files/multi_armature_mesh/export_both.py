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
    from io_ggltf.Advanced import *
    from io_ggltf.Constants import *

    filePath = "//..\\..\\output\\"
    fileName = "multi_armature_mesh_export_both"
    binPath = ""

    def test(bucket):
        Settings.set_setting(bucket, BUCKET_SETTING_NODE_AUTO_ATTACH_DATA, False)
        Settings.set_setting(bucket, BUCKET_SETTING_MESH_AUTO_ATTACH, False)
        Settings.set_setting(bucket, BUCKET_SETTING_SKIN_AUTO_ATTACH, False)
        node = Node.based_on_object(bucket, "MeshObj")
        skin = Skin.based_on_object_modifiers(bucket, "MeshObj", getInverseBinds=True, forceRestPose=True)
        mesh = Mesh.based_on_object(bucket, "MeshObj", skinID=skin, uvMaps=False)
        Attach.skin_to_node(bucket, skin, node)
        Attach.mesh_to_node(bucket, mesh, node)
        File.dump_bucket(bucket)

    print("---------- Start gltf embedded")
    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    print("---------- Start gltf with external binaries")
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    print("---------- Start glb")
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))
