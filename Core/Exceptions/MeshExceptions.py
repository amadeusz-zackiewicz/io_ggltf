class MissingMeshComponentException(Exception):
    def __init__(self, objName: str, missing: list[str], context: str):
        self.__objName = objName
        self.__missing = missing
        self.__context = context

    def __str__(self):
        missing = [f'"{m}"' for m in self.__missing]
        return f"""An exception has occured due to missing mesh components:
            {self.__context} from '{self.__objName}':
                {", ".join(missing)}"""

class MissingUVMapsException(MissingMeshComponentException):
    def __init__(self, objName: str, missing: list[str]):
        super().__init__(objName=objName, missing=missing, context="Missing UV Maps")

class MissingVertexColorsException(MissingMeshComponentException):
    def __init__(self, objName: str, missing: list[str]):
        super().__init__(objName=objName, missing=missing, context="Missing Vertex Colors")

class MissingShapeKeysException(MissingMeshComponentException):
    def __init__(self, objName: str, missing: list[str]):
        super().__init__(objName, missing, context="Missing Shape Keys")

class MeshComponentValidationFailedException(Exception):
    def __str__(self):
        return "Mesh validation has failed, check below for details"