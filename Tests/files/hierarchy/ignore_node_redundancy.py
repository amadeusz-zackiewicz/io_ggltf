from io_ggltf.Advanced import Node
from io_ggltf.Advanced import File
from io_ggltf.Advanced import Settings

from io_ggltf.Keywords import FILE_TYPE_GLTF_EMBEDDED, FILE_TYPE_GLB, FILE_TYPE_GLTF, BUCKET_SETTING_REDUNDANCY_CHECK_NODE

filePath = "//..\\..\\output\\"
fileName = "hierarchy_ignore_node_redundancy"
binPath = ""

def test(bucket):
    Settings.set_setting(bucket, BUCKET_SETTING_REDUNDANCY_CHECK_NODE, False)
    Node.based_on_hierarchy(bucket, "0-0")
    Node.based_on_hierarchy(bucket, "0-0")
    Node.based_on_hierarchy(bucket, "1-0")
    Node.based_on_hierarchy(bucket, "4-4")
    File.dump_bucket(bucket)

test(File.create_bucket(filePath, fileName + "_embedded", binPath, FILE_TYPE_GLTF_EMBEDDED))
test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLTF))
test(File.create_bucket(filePath, fileName, binPath, FILE_TYPE_GLB))