from io_ggltf.Core import Util

class AnimationDescriber:
    from io_ggltf.Constants import BUCKET_DATA_SKINS, SKIN_JOINTS
    def __init__(self, name: str, frameStart=None, frameEnd=None, frameStep=1.0, useStepInterpolation=False, optimiseKeys=True):
        self.__name = name
        self.__frameStart = frameStart
        self.__frameEnd = frameEnd
        self.__map = {}
        self.__extraTracks = set()
        self.__nodes = set()
        self.__hierarchies = set()
        self.__scenes = set()
        self.__skins = set()
        self.__frameStep = frameStep
        self.__stepInter = useStepInterpolation
        self.__optimise = optimiseKeys

    def add_track(self, objAccessor, trackName):
        """
        Add NLA track to the describer.

        Args:
            objAccessor (tuple[str, str] or str): Accessor pointing to an object that contains the track.
            Setting it to none will instead add the track name to global list.
            trackName (list[str] or str): Names of the tracks to be included.
        """
        if type(objAccessor) == str:
            objAccessor = (objAccessor, None)

        if type(trackName) == str:
            trackName = {trackName}

        if objAccessor == None:
            self.__extraTracks.update(trackName)
        else:
            if objAccessor in self.__map:
                self.__map[objAccessor].update(trackName)
            else:
                self.__map[objAccessor] = trackName

    def add_node(self, nodeID: int):
        self.__nodes.add(nodeID)

    def add_node_hierarchy(self, topNodeID: int):
        self.__hierarchies.add(topNodeID)

    def add_scene(self, sceneID: int):
        self.__scenes.add(sceneID)

    def add_skin(self, skinID: int):
        self.__skins.add(skinID)

    def _get_nodes(self, bucket):
        """
        Get ID of all nodes in the added scenes, hierarchies, solo nodes or skins. 
        It achieves it by scanning the node tree inside a staged bucket.

        For internal use only
        """
        nodes = set()

        for scene in self.__scenes:
            nodes.update(Util.get_all_nodes_in_scene(bucket, scene))

        for hierarchy in self.__hierarchies:
            nodes.update(Util.get_all_nodes_in_hierarchy(bucket, hierarchy))

        for node in self.__nodes:
            nodes.add(node)
        
        for skinID in self.__skins:
            skin = bucket.data[self.BUCKET_DATA_SKINS][skinID]
            nodes.update(skin[self.SKIN_JOINTS])

        return nodes

    def _get_map(self):
        """
        Get a dictionary that describes which NLA tracks needed to be enabled for this animation.

        For internal use only
        """
        return self.__map

    def _get_extra_tracks(self):
        return self.__extraTracks

    def _get_name(self):
        """
        For internal use only
        """
        return self.__name

    def _get_frame_range(self):
        """
        For internal use only
        """
        return self.__frameStart, self.__frameEnd

    def _get_frame_step(self):
        """
        For internal use only
        """
        return self.__frameStep

    def _use_step_interpolation(self):
        """
        For internal use only
        """
        return self.__stepInter

    def _optimise(self):
        """
        For internal use only
        """
        return self.__optimise

    def copy(self):
        newDesc = AnimationDescriber(self.__name, self.__frameStart, self.__frameEnd, self.__frameStep, self.__stepInter, self.__optimise)
        newDesc.__nodes = self.__nodes.copy()
        newDesc.__hierarchies = self.__hierarchies.copy()
        newDesc.__scenes = self.__scenes.copy()
        newDesc.__skins = self.__skins.copy()
        newDesc.__map = self.__map.copy()
        newDesc.__extraTracks = self.__extraTracks.copy()

        return newDesc