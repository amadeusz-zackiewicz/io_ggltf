from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core import Linker

__node_to_node_command = lambda bucket, child, parent:  Linker.node_to_node(bucket=bucket, parentID=parent, childID=child)
__mesh_to_node_command = lambda bucket, mesh, node, override: Linker.mesh_to_node(bucket=bucket, meshID=mesh, nodeID=node, override=override)
__skin_to_node_command = lambda bucket, skin, node, override: Linker.skin_to_node(bucket=bucket, skinID=skin, nodeID=node, override=override)

def node_to_node(bucket: Bucket, childNodeID: int, parentNodeID: int):
    bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__node_to_node_command, (bucket, childNodeID, parentNodeID)))

def mesh_to_node(bucket: Bucket, meshID: int, nodeID: int, forceOverride = True):
    bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__mesh_to_node_command, (bucket, meshID, nodeID, forceOverride)))

def skin_to_node(bucket: Bucket, skinID: int, nodeID: int, forceOverride = True):
    bucket.commandQueue[COMMAND_QUEUE_LINKER].append((__skin_to_node_command, (bucket, skinID, nodeID, forceOverride)))