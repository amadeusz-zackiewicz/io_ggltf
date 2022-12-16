class TimelineMarkerException(Exception):
    def __init__(self, markerName: str) -> None:
        self.__markerName = markerName

    def __str__(self) -> str:
        return f"Timeline marker with name '{self.__markerName}' was not found."