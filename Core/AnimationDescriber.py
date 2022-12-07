from io_ggltf.Core import Util

class AnimationDescriber:
    def __init__(self, name: str, frameStart=None, frameEnd=None, objAccessor=None, trackName=None):
        self.__name = name
        self.__frameStart = frameStart
        self.__frameEnd = frameEnd
        self.__map = {}
        self.__nodes = set()
        self.__hierarchies = set()
        self.__scenes = set()

        if objAccessor != None and trackName !=None:
            self.add_track(objAccessor, trackName)

    def add_track(self, objAccessor, trackName):
        """
        Add NLA track to the describer.

        Args:
            objAccessor (tuple[str, str] or str): Accessor pointing to an object that contains the track.
            trackName (list[str] or str): Names of the tracks to be included.
        """
        if type(objAccessor) == str:
            objAccessor = (objAccessor, None)

        if type(trackName) == str:
            trackName = [trackName]

        if objAccessor in self.__map:
            self.__map[objAccessor].extend(trackName)
        else:
            self.__map[objAccessor] = trackName

    def add_node(self, nodeID: int):
        self.__nodes.add(nodeID)

    def add_node_hierarchy(self, topNodeID: int):
        self.__hierarchies.add(topNodeID)

    def add_scene(self, sceneID: int):
        self.__scenes.add(sceneID)

    def _get_nodes(self, bucket):
        """
        Get ID of all nodes in the added scenes, hierarchies or solo nodes. 
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

        return nodes

    def _get_map(self):
        """
        Get a dictionary that describes which NLA tracks needed to be enabled for this animation.

        For internal use only
        """
        return self.__map

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

    def copy(self):
        newDesc = AnimationDescriber(self.__frameStart, self.__frameEnd)
        newDesc.__map = self.__map.copy()