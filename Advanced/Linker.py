from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core import Linker, Util, BlenderUtil
from io_ggltf.Core.Managers import RedundancyManager as RM

__node_to_node_command = lambda bucket, child, parent:  Linker.node_to_node(bucket=bucket, parentID=parent, childID=child)
__mesh_to_node_command = lambda bucket, mesh, node, override: Linker.mesh_to_node(bucket=bucket, meshID=mesh, nodeID=node, override=override)
__skin_to_node_command = lambda bucket, skin, node, override: Linker.skin_to_node(bucket=bucket, skinID=skin, nodeID=node, override=override)

def node_to_node(bucket: Bucket, childNodeID: int, parentNodeID: int):
    bucket.commandQueue[__k.COMMAND_QUEUE_LINKER].append((__node_to_node_command, (bucket, childNodeID, parentNodeID)))

def mesh_to_node(bucket: Bucket, meshID: int, nodeID: int, forceOverride = True):
    bucket.commandQueue[__k.COMMAND_QUEUE_LINKER].append((__mesh_to_node_command, (bucket, meshID, nodeID, forceOverride)))

def skin_to_node(bucket: Bucket, skinID: int, nodeID: int, forceOverride = True):
    bucket.commandQueue[__k.COMMAND_QUEUE_LINKER].append((__skin_to_node_command, (bucket, skinID, nodeID, forceOverride)))

def node_to_node_unsafe(bucket: Bucket, childNodeAccessor, parentNodeAccessor):
    childNode = RM.fetch_last_id_from_unsafe(bucket, childNodeAccessor, __k.BUCKET_DATA_NODES)
    parentNode = RM.fetch_last_id_from_unsafe(bucket, parentNodeAccessor, __k.BUCKET_DATA_NODES)
    node_to_node(bucket, childNode, parentNode)

def mesh_to_node_unsafe(bucket: Bucket, meshAccessor, nodeAccessor):
    mesh = RM.fetch_last_id_from_unsafe(bucket, meshAccessor, __k.BUCKET_DATA_MESHES)
    node = RM.fetch_last_id_from_unsafe(bucket, nodeAccessor, __k.BUCKET_DATA_NODES)
    mesh_to_node(bucket, mesh, node)

def skin_to_node_unsafe(bucket: Bucket, skinAccessor, nodeAccessor):
    skin = RM.fetch_last_id_from_unsafe(bucket, skinAccessor, __k.BUCKET_DATA_SKINS)
    node = RM.fetch_last_id_from_unsafe(bucket, nodeAccessor, __k.BUCKET_DATA_NODES)
    skin_to_node(bucket, skin, node)

    