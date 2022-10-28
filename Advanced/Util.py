from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import create_filter, pattern_replace as __replace
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI

@__ShowInUI
def pattern_replace_node_names(bucket: Bucket, pattern: str, replacement: str):
    bucket.commandQueue[__c.COMMAND_QUEUE_NAMING].append((__replace, (bucket, __c.BUCKET_DATA_NODES, pattern, replacement)))

@__ShowInUI
def pattern_replace_mesh_names(bucket: Bucket, pattern: str, replacement: str):
    bucket.commandQueue[__c.COMMAND_QUEUE_NAMING].append((__replace, (bucket, __c.BUCKET_DATA_MESHES, pattern, replacement)))

@__ShowInUI
def pattern_replace_all_names(bucket: Bucket, pattern: str, replacement: str):
    pattern_replace_node_names(bucket, pattern, replacement)
    pattern_replace_mesh_names(bucket, pattern, replacement)