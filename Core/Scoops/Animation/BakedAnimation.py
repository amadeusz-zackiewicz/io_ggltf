from io_ggltf.Core.AnimationDescriber import AnimationDescriber
from io_ggltf.Core.Blender import NLA, Timeline
from io_ggltf.Core.Bucket import Bucket

class BakedAnimation():
    def __init__(self, bucket: Bucket, animDescriber: AnimationDescriber):
        """
        Bake animation tracks based on the describer and store them within.

        Args:
            bucket (Bucket): Bucket to reference nodes from
            startFrame (int): Frame from which the bake will start
            endFrame (int): Frame from which the bake will end
            nodeIDs (list[int]): Nodes to include in this animation
            sceneID (int): Scene to get nodes from if nodes are blank
        """
        self.bakedAnim = {}

        self.name = animDescriber._get_name()
        startFrame, endFrame = animDescriber.get_frame_range()

        nodes = animDescriber._get_nodes(bucket)
        nlaMap = animDescriber._get_map()

        if startFrame == None or endFrame == None:
            newStart, newEnd = NLA.get_framerange_for_map(nlaMap)
            if startFrame == None:
                startFrame = newStart
            if endFrame == None:
                endFrame = newEnd

        step = animDescriber._get_frame_step()

        if Timeline.is_frame_step_valid(startFrame, endFrame, step):
            self.__bake(bucket, startFrame=startFrame, endFrame=endFrame, nodeIDs=nodes, step=step)

    def get_animation(self):
        return self.bakedAnim

    def __bake(self, bucket: Bucket, startFrame: float, endFrame: float, nodeIDs: list, step: float, clean: bool):
        """
        Bake all nodes based on their viewport evaluation

        Args:
            bucket (Bucket):
            startFrame (float): Frame from which to start baking.
            endFrame (float): Frame on which to stop the bake

        """
        # Initialise the dictionary that will be used to store animation temporarily
        # Dictionary will consist of 
        #
        # Dict[NodeID]
        #       Dict[NodeProperty]
        #               Tuple[Time, Value]
        #
        # Which is enough information to add samplers and buffers from
        nodeAnim = {}
        for nodeID in nodeIDs:
            properties = bucket.nodeProperties[nodeID]
            propDict = {}
            for prop in properties:
                propDict[prop] = []
            nodeAnim[nodeID] = propDict

        