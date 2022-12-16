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
        if self.__step == 0.0:
            return "Frame step can not be set to 0.0"
        if self.__step < 0.0:
            return f"Frame step can not be negative ({self.__step})"
        return f"Failed to divide frame range of {self.__end - self.__start}(Start:{self.__end} - End:{self.__start}) by {self.__step}."