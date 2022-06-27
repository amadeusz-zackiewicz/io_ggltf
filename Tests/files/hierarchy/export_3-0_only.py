from io_advanced_gltf2.Advanced import Node
from io_advanced_gltf2.Advanced import File

from io_advanced_gltf2.Keywords import FILE_TYPE_GLTF_EMBEDDED, FILE_TYPE_GLB, FILE_TYPE_GLTF

filePath = "//..\\..\\output\\"
fileName = "hierarchy_export_3-0_only"
binPath = ""

def test(bucket):
    Node.based_on_hierarchy(bucket, "3-0")
    File.dump_bucket(bucket)

test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))