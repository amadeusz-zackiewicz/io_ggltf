from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI

@__ShowInUI
def create(bucket: Bucket, name = None, nodes = []) -> int:

    scene = {__c.SCENE_NODES: nodes}
    if name != None:
        scene[__c.SCENE_NAME] = name
    sceneID = len(bucket.data[__c.BUCKET_DATA_SCENES])
    bucket.data[__c.BUCKET_DATA_SCENES].append(scene)

    return sceneID

@__ShowInUI
def append_node(bucket: Bucket, sceneIDs: list or int, nodeIDs: list or int):
    if type(sceneIDs) == int:
        sceneIDs = [sceneIDs]

    if type(nodeIDs) == int:
        nodeIDs = [nodeIDs]

    for sceneID in sceneIDs:
        scene = bucket.data[__c.BUCKET_DATA_SCENES][sceneID]

        for nodeID in nodeIDs:
            if nodeID not in scene[__c.SCENE_NODES]:
                scene[__c.SCENE_NODES].append(nodeID)

@__ShowInUI
def set_default(bucket: Bucket, sceneID: int):
    bucket.data["scene"] = sceneID