from io_advanced_gltf2.Advanced import Node
from io_advanced_gltf2.Advanced import File
from io_advanced_gltf2.Advanced import Settings

from io_advanced_gltf2.Keywords import FILE_TYPE_GLTF_EMBEDDED, FILE_TYPE_GLB, FILE_TYPE_GLTF, BUCKET_SETTING_REDUNDANCY_CHECK_NODE

filePath = "//..\\..\\output\\"
fileName = "hierarchy_check_node_redundancy"
binPath = ""

def test(bucket):
    Settings.set_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE, True)
    Node.based_on_hierarchy(bucket, "0-0")
    Node.based_on_hierarchy(bucket, "0-0")
    Node.based_on_hierarchy(bucket, "1-0")
    Node.based_on_hierarchy(bucket, "4-4")
    File.dump_bucket(bucket)

test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))