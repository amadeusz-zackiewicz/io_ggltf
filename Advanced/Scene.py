from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core import ShowFunction
from warnings import deprecated

@deprecated("Advanced.Scene.create is deprecated, it will be removed in future versions and might not function as intended.")
def create(bucket: Bucket, name = None, nodes = []) -> int:
    """Create a new scene"""

    scene = {__c.SCENE_NODES: nodes}
    if name != None:
        scene[__c.SCENE_NAME] = name
    sceneID = len(bucket.data[__c.BUCKET_DATA_SCENES])
    bucket.data[__c.BUCKET_DATA_SCENES].append(scene)

    return sceneID

@deprecated("Advanced.Scene.append_node is deprecated, it will be removed in future versions and might not function as intended.")
def append_node(bucket: Bucket, sceneIDs: list or int, nodeIDs: list or int):
    """Append node to the scene"""

    if type(sceneIDs) == int:
        sceneIDs = [sceneIDs]

    if type(nodeIDs) == int:
        nodeIDs = [nodeIDs]

    for sceneID in sceneIDs:
        scene = bucket.data[__c.BUCKET_DATA_SCENES][sceneID]

        for nodeID in nodeIDs:
            if nodeID not in scene[__c.SCENE_NODES]:
                scene[__c.SCENE_NODES].append(nodeID)

@deprecated("Advanced.Scene.set_default is deprecated, it will be removed in future versions and might not function as intended.")
def set_default(bucket: Bucket, sceneID: int):
    """Select the scene that will be shown by first in most programs"""

    bucket.data["scene"] = sceneID

#ShowFunction.Register(create, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Scene-Module#create")
#ShowFunction.Register(append_node, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Scene-Module#append_node")
#ShowFunction.Register(set_default, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Scene-Module#set_default")