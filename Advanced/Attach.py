from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core import Linker, Util, BlenderUtil, ShowFunction
from io_ggltf.Core.Managers import RedundancyManager as RM

__node_to_node_command = lambda bucket, child, parent:  Linker.node_to_node(bucket=bucket, parentID=parent, childID=child)
__mesh_to_node_command = lambda bucket, mesh, node, override: Linker.mesh_to_node(bucket=bucket, meshID=mesh, nodeID=node, override=override)
__skin_to_node_command = lambda bucket, skin, node, override: Linker.skin_to_node(bucket=bucket, skinID=skin, nodeID=node, override=override)

def node_to_node(bucket: Bucket, childNodeID: int, parentNodeID: int):
    """Make one node become child of the other node"""
    bucket.commandQueue[__c.COMMAND_QUEUE_LINKER].append((__node_to_node_command, (bucket, childNodeID, parentNodeID)))

def mesh_to_node(bucket: Bucket, meshID: int, nodeID: int, forceOverride = True):
    """Add mesh data to a node"""
    bucket.commandQueue[__c.COMMAND_QUEUE_LINKER].append((__mesh_to_node_command, (bucket, meshID, nodeID, forceOverride)))

def skin_to_node(bucket: Bucket, skinID: int, nodeID: int, forceOverride = True):
    """Add skin data to a node"""
    bucket.commandQueue[__c.COMMAND_QUEUE_LINKER].append((__skin_to_node_command, (bucket, skinID, nodeID, forceOverride)))

def node_to_node_unsafe(bucket: Bucket, childNodeAccessor, parentNodeAccessor):
    """Make one node become child of the other node without knowing their IDs"""
    childNode = RM.fetch_last_id_from_unsafe(bucket, childNodeAccessor, __c.BUCKET_DATA_NODES)
    parentNode = RM.fetch_last_id_from_unsafe(bucket, parentNodeAccessor, __c.BUCKET_DATA_NODES)
    node_to_node(bucket, childNode, parentNode)

def mesh_to_node_unsafe(bucket: Bucket, meshAccessor, nodeAccessor):
    """Attach a mesh to node without knowing their IDs"""
    mesh = RM.fetch_last_id_from_unsafe(bucket, meshAccessor, __c.BUCKET_DATA_MESHES)
    node = RM.fetch_last_id_from_unsafe(bucket, nodeAccessor, __c.BUCKET_DATA_NODES)
    mesh_to_node(bucket, mesh, node)

def skin_to_node_unsafe(bucket: Bucket, skinAccessor, nodeAccessor):
    """Attach a skin to node without knowing their IDs"""
    skin = RM.fetch_last_id_from_unsafe(bucket, skinAccessor, __c.BUCKET_DATA_SKINS)
    node = RM.fetch_last_id_from_unsafe(bucket, nodeAccessor, __c.BUCKET_DATA_NODES)
    skin_to_node(bucket, skin, node)

def skin_to_unsafe_node(bucket: Bucket, skinID, nodeAccessor):
    """If you know the ID of the skin but not the node"""
    node = RM.fetch_last_id_from_unsafe(bucket, nodeAccessor, __c.BUCKET_DATA_NODES)
    skin_to_node(bucket, skinID, node)

def mesh_to_unsafe_node(bucket: Bucket, meshID, nodeAccessor):
    """If you know the ID of the mesh but not the node"""
    node = RM.fetch_last_id_from_unsafe(bucket, nodeAccessor, __c.BUCKET_DATA_NODES)
    mesh_to_node(bucket, meshID, node)

ShowFunction.Register(node_to_node, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#node_to_node")
ShowFunction.Register(mesh_to_node, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#mesh_to_node")
ShowFunction.Register(skin_to_node, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#skin_to_node")
ShowFunction.Register(node_to_node_unsafe, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#node_to_node_unsafe")
ShowFunction.Register(mesh_to_node_unsafe, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#mesh_to_node_unsafe")
ShowFunction.Register(skin_to_node_unsafe, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#skin_to_node_unsafe")
ShowFunction.Register(skin_to_unsafe_node, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#skin_to_unsafe_node")
ShowFunction.Register(mesh_to_unsafe_node, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Attach-Module#mesh_to_unsafe_node")