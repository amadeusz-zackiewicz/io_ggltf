class TimelineMarkerException(Exception):
    def __init__(self, markerName: str) -> None:
        self.__markerName = markerName

    def __str__(self) -> str:
        return f"Timeline marker with name '{self.__markerName}' was not found."

class InvalidFrameStepException(Exception):
    def __init__(self, start, end, step) -> None:
        self.__start = start
        self.__end = end
        self.__step = step

    def __str__(self) -> str:
        return f"Failed to divide frame range of {self.__end - self.__start}({self.__end} - {self.__start}) by {self.__step}."