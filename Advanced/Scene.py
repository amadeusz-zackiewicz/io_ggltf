from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket

def create(bucket: Bucket, name = None, nodes = []) -> int:

    scene = {__c.SCENE_NODES: nodes}
    if name != None:
        scene[__c.SCENE_NAME] = name
    sceneID = len(bucket.data[__c.BUCKET_DATA_SCENES])
    bucket.data[__c.BUCKET_DATA_SCENES].append(scene)

    return sceneID

def append_node(bucket: Bucket, sceneID: int, nodeIDs: list or int):
    if type(nodeIDs) == int:
        nodeIDs = [nodeIDs]

    scene = bucket.data[__c.BUCKET_DATA_SCENES][sceneID]

    for nodeID in nodeIDs:
        if nodeID not in scene[__c.SCENE_NODES]:
            scene[__c.SCENE_NODES].append(nodeID)