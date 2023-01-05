from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Util import create_filter as __create_filter, pattern_replace as __replace
from io_ggltf.Core import ShowFunction

def pattern_replace_node_names(bucket: Bucket, pattern: str, replacement: str):
    """Replace all node names based on the pattern"""
    bucket.commandQueue[__c.COMMAND_QUEUE_NAMING].append((__replace, (bucket, __c.BUCKET_DATA_NODES, pattern, replacement)))

def pattern_replace_mesh_names(bucket: Bucket, pattern: str, replacement: str):
    """Replace all mesh names based on the pattern"""
    bucket.commandQueue[__c.COMMAND_QUEUE_NAMING].append((__replace, (bucket, __c.BUCKET_DATA_MESHES, pattern, replacement)))

def pattern_replace_all_names(bucket: Bucket, pattern: str, replacement: str):
    """Replace all mesh and node names based on the pattern"""
    pattern_replace_node_names(bucket, pattern, replacement)
    pattern_replace_mesh_names(bucket, pattern, replacement)

def create_filter(pattern: str, whitelist=True):
    return __create_filter(pattern=pattern, whitelist=whitelist)

ShowFunction.Register(pattern_replace_node_names, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Util-Module#pattern_replace_node_names")
ShowFunction.Register(pattern_replace_mesh_names, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Util-Module#pattern_replace_mesh_names")
ShowFunction.Register(pattern_replace_all_names, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Util-Module#pattern_replace_all_names")
ShowFunction.Register(create_filter, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Util-Module#create_filter")