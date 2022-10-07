from io_ggltf.Constants import *
from io_ggltf.Core.Bucket import Bucket

class OutOfBoundsException(Exception):
    """Given Object ID is not valid"""
    def __init__(self, context: str, min: int, max: int, value: int):
        self.message = f"{context} is out of bounds, Range({min}, {max - 1}), value given: {value}"
        super().__init__(self.message)


def node_to_node(bucket: Bucket, parentID: int, childID: int):
    nodes = bucket.data[BUCKET_DATA_NODES]
    if not parentID in range(len(nodes)):
        raise OutOfBoundsException("Parent ID", 0, len(nodes), parentID)

    if not childID in range(len(nodes)):
        raise OutOfBoundsException("Child ID", 0, len(nodes), childID)

    parentNode = nodes[parentID]
    if NODE_CHILDREN in parentNode:
        parentNode[NODE_CHILDREN].append(childID)
    else:
        parentNode[NODE_CHILDREN] = [childID]

def mesh_to_node(bucket: Bucket, meshID: int, nodeID: int, override = True):
    nodes = bucket.data[BUCKET_DATA_NODES]
    
    if not nodeID in range(len(nodes)):
        raise OutOfBoundsException("Node ID", 0, len(nodes), nodeID)

    if not meshID in range(len(bucket.data[BUCKET_DATA_MESHES])):
        raise OutOfBoundsException("Mesh ID", 0, len(bucket.data[BUCKET_DATA_MESHES]), meshID)

    node = nodes[nodeID]

    if NODE_MESH in node:
        if override:
            node[NODE_MESH] = meshID
    else:
        node[NODE_MESH] = meshID

def skin_to_node(bucket: Bucket, skinID: int, nodeID: int, override = True):
    nodes = bucket.data[BUCKET_DATA_NODES]

    if not nodeID in range(len(nodes)):
        raise OutOfBoundsException("Node ID", 0, len(nodes), nodeID)

    if not skinID in range(len(bucket.data[BUCKET_DATA_SKINS])):
        raise OutOfBoundsException("Skin ID", 0, len(bucket.data[BUCKET_DATA_SKINS]), skinID)

    node = nodes[nodeID]

    if NODE_SKIN in node:
        if override:
            node[NODE_SKIN] = skinID
    else:
        node[NODE_SKIN] = skinID

def weights_to_node(bucket: Bucket, weights: list, nodeID, override = True):
    nodes = bucket.data[BUCKET_DATA_NODES]

    if not nodeID in range(len(nodes)):
        raise OutOfBoundsException("Node ID", 0, len(nodes), nodeID)

    node = nodes[nodeID]

    if NODE_WEIGHTS in node:
        if override:
            node[NODE_WEIGHTS] = weights
    else:
        node[NODE_WEIGHTS] = weights
