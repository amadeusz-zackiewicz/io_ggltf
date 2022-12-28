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
        self._bakedAnim = {}

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

        if Timeline.is_frame_step_valid(startFrame, endFrame, step):
            NLA.prep_tracks_for_animation(nlaMap, extraTracks)
            self.__bake(bucket, startFrame=startFrame, endFrame=endFrame, nodeIDs=animDescriber._get_nodes(bucket), step=step, clean=animDescriber._optimise())

    def get_animation(self):
        return self._bakedAnim

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
        #                                   list[list[Time], list[Value]]]]
        #
        # Which is enough information to add samplers and buffers from

        bake = {}
        for nodeID in nodeIDs:
            properties = bucket.nodeProperties[nodeID]
            propDict = {}
            for prop in properties:
                propDict[prop] = [[], []]
            bake[nodeID] = propDict

        possibleSteps = int((endFrame - startFrame) / step)
        frames = [float(s) * step for s in range(possibleSteps)]

        for frame in frames:
            Timeline.set_frame(frame + startFrame, bucket.currentDependencyGraph)
            time = Timeline.get_real_time(frame)
            for nodeID, properties in bake.items():
                for property, keyframes in properties.items():
                    value = Properties.get_property(bucket, nodeID, property)
                    if value != None:
                        keyframes[0].append(time)
                        keyframes[1].append(value)
                        #print(f"{nodeID}({property}): {time} - {value}")

        if clean:
            for nodeID, properties in bake.items():
                for property, keyframes in properties.items():
                    popKey = []
                    for i, keyframe in enumerate(keyframes[1]):
                        if i == 0: continue
                        if i == len(keyframes[1]) - 1: continue
                        leftKeyframe = keyframes[1][i - 1]
                        rightKeyframe = keyframes[1][i + 1]
                        if leftKeyframe == keyframe and rightKeyframe == keyframe:
                            popKey.append(i)
                    for p in reversed(popKey):
                        del keyframes[0][p]
                        del keyframes[1][p]

                removeProperty = []
                for property, keyframes in properties.items():
                    if len(keyframes[0]) == 0:
                        removeProperty.append(property)
                for p in removeProperty:
                    del properties[p]

        self._bakedAnim = bake