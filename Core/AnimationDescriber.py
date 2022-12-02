
class AnimationDescriber:
    def __init__(self, frameStart = None, frameEnd=None):
        self._frameStart = frameStart
        self._frameEnd = frameEnd
        self._map = {}

    def add_track(self, objAccessor, trackName):
        if type(objAccessor) == str:
            objAccessor = (objAccessor, None)

        if type(trackName) == str:
            trackName = [trackName]

        if objAccessor in self._map:
            self._map[objAccessor].extend(trackName)
        else:
            self._map[objAccessor] = trackName

    def get_map(self):
        return self._map

    def copy(self):
        newDesc = AnimationDescriber(self._frameStart, self._frameEnd)
        newDesc._map = self._map.copy()