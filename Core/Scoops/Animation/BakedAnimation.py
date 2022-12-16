from io_ggltf.Core.AnimationDescriber import AnimationDescriber
from io_ggltf.Core.Blender import NLA, Timeline
from io_ggltf.Core.Scoops.Animation import Properties
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
        startFrame, endFrame = animDescriber._get_frame_range()

        nlaMap = animDescriber._get_map()
        extraTracks = animDescriber._get_extra_tracks()

        if type(startFrame) == str:
            startFrame = Timeline.get_marker_frame(startFrame)
        if type(endFrame) == str:
            endFrame = Timeline.get_marker_frame(endFrame)

        if startFrame == None or endFrame == None:
            newStart, newEnd = NLA.get_framerange(nlaMap, extraTracks)
            if startFrame == None:
                startFrame = newStart
            if endFrame == None:
                endFrame = newEnd

        step = animDescriber._get_frame_step()
        print("Frame range:", startFrame, endFrame)
        if Timeline.is_frame_step_valid(startFrame, endFrame, step):
            NLA.prep_tracks_for_animation(nlaMap, extraTracks)
            print("Animation Map:", nlaMap)
            print("Extra tracks:", extraTracks)
            self.__bake(bucket, startFrame=startFrame, endFrame=endFrame, nodeIDs=animDescriber._get_nodes(bucket), step=step, clean=False)
        else:
            raise Exception("Invalid frame step")

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
        # Dict[NodeID: 
        #               Dict[NodeProperty: 
        #                                   list[list[Time, Value]]]]
        #
        # Which is enough information to add samplers and buffers from

        nodeAnim = {}
        for nodeID in nodeIDs:
            properties = bucket.nodeProperties[nodeID]
            propDict = {}
            for prop in properties:
                propDict[prop] = [[], []]
            nodeAnim[nodeID] = propDict
        
        possibleSteps = int((endFrame - startFrame) / step)
        frames = [float(s) * step for s in range(possibleSteps)]

        for frame in frames:
            for nodeID, properties in nodeAnim.items():
                for property, data in properties.items():
                    Timeline.set_frame(frame + startFrame)
                    value = Properties.get_property(bucket, nodeID, property)
                    if value != None:
                        time = Timeline.get_real_time(frame)
                        data[0].append(time)
                        data[1].append(value)
                        #print(f"{nodeID}({property}): {time} - {value}")

        print(nodeAnim) 