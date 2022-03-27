import functools

@functools.total_ordering
class Compound:
    def __init__(self, position, normal, tangent, uvPos, vColor, shapes):
        self.position = position
        self.normal = normal
        self.tangent = tangent
        self.uv = uvPos
        self.color = vColor
        self.shapes = shapes

    def __lt__(a, b):
        return a.position < b.position

    def __gt__(a, b):
        return a.position > b.position

    def __eq__(a, b):
        if a.position.x != b.position.x or a.position.y != b.position.y or a.position.z != b.position.z: return False
        if a.normal.x != b.normal.x or a.normal.y != b.normal.y or a.normal.z != b.normal.z: return False
        for i in range(len(a.uv)):
            if a.uv[i].x != b.uv[i].x or a.uv[i].y != b.uv[i].y: return False
        for i in range(len(a.vColor)):
            for vc_i in range(len(a.vColor)):
                if a.vColor[i][vc_i] != b.vColor[i][vc_i]: return False
        return True

class Primitive:
    def __init__(self, uvMapCount = 0, vertexColorCount = 0, shapeKeyCount = 0):
        self.positions = []
        self.normals = []
        self.tangents = []
        self.indices = []
        self.duplicates = {}
        self.uv = [[]] * uvMapCount
        self.vertexColor = [[]] * vertexColorCount
        self.shapKey = [[]] * shapeKeyCount