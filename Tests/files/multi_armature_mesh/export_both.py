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
