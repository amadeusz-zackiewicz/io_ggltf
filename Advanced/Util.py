from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import create_filter, pattern_replace as __replace

def pattern_replace_node_names(bucket: Bucket, pattern: str, replacement: str):
    bucket.commandQueue[__k.COMMAND_QUEUE_NAMING].append((__replace, (bucket, __k.BUCKET_DATA_NODES, pattern, replacement)))

def pattern_replace_mesh_names(bucket: Bucket, pattern: str, replacement: str):
    bucket.commandQueue[__k.COMMAND_QUEUE_NAMING].append((__replace, (bucket, __k.BUCKET_DATA_MESHES, pattern, replacement)))

def pattern_replace_all_names(bucket: Bucket, pattern: str, replacement: str):
    pattern_replace_node_names(bucket, pattern, replacement)
    pattern_replace_mesh_names(bucket, pattern, replacement)