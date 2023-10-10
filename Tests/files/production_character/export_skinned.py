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
    from io_ggltf.Advanced import *
    from io_ggltf.Constants import *

    filePath = "//..\\..\\output\\"
    fileName = "production_character_export_skinned"
    binPath = ""

    meshNames = ["LP_Body", "LP_Jacket", "LP_Jacket_tear", "LP_Hair", "LP_Hand.L", "LP_Hand.R", "LP_Armband", "LP_Belt", "LP_Boots", "LP_Face_features", "LP_Eye_Whites", "LP_eyes", "LP_Teeth", "LP_Tongue", "LP_Belt_tip"]

    def test(bucket):
        skin, _ = Skin.based_on_object(bucket, "RIG-trashblazer_f_meta", autoAttach=False, getInverseBinds=True)
        node = Node.dummy(bucket, "trashblazer_f")
    
        mesh = Mesh.merged_based_on_list(bucket, meshNames, blacklist={}, name='trashblazer_f', uvMaps=["UVMap"], skinID=skin)
        Attach.mesh_to_node(bucket, mesh, node, forceOverride=True)
        Attach.skin_to_node(bucket, skin, node, forceOverride=True)
        File.dump_bucket(bucket)

    print("---------- Start gltf embedded")
    test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
    print("---------- Start gltf with external binaries")
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
    print("---------- Start glb")
    test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))
