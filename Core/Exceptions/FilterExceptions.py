
class IncorrectFilterFormatException(Exception):
    def __init__(self, arg):
        self.argType = type(arg)
        if type(arg) == tuple:
            self.tupTypes = [type(v) for v in arg]
        else:
            self.tupTypes = None

    def __str__(self):
        if self.argType != tuple:
            return f"Filter Format Error: Expected types: 'tuple[str, bool]', got: '{self.argType}'"
        else:
            return f"Filter Fromat Error: Expected types: 'tuple[str, bool]', got: '{self.argType}[{', '.join(self.tupTypes)}]'"

class IncorrectFilterTypeException(Exception):
    def __init__(self, arg) -> None:
        self.argType = type(arg)

    def __str__(self) -> str:
        return f"Filter Type Error: Expected types: 'tuple[str, bool]' or 'list[tuple[str, bool]]', got: {self.argType}"
