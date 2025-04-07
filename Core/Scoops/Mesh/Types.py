import functools

@functools.total_ordering
class Compound:
    def __init__(self, position, normal, tangent, uvPos, vColor, shapeKey, boneID, boneInfluence):
        self.position = position
        self.normal = normal
        self.tangent = tangent
        self.uv = uvPos
        self.color = vColor
        self.shapeKey = shapeKey
        self.boneID = boneID
        self.boneInfluence = boneInfluence

    def __lt__(a, b):
        return a.position < b.position

    def __gt__(a, b):
        return a.position > b.position

    def __eq__(a, b):
        for i in range(3): # compare position
            if a.position[i] != b.position[i]: return False
        for i in range(3): # compare normals
            if a.normal[i] != b.normal[i]: return False
        for i in range(len(a.uv)): # compare each uv
            if a.uv[i].x != b.uv[i].x or a.uv[i].y != b.uv[i].y: return False
        for i in range(len(a.color)): # compare each vertex color
            for vc_i in range(len(a.color)):
                if a.color[i][vc_i] != b.color[i][vc_i]: return False
        for i in range(len(a.shapeKey)): # compare shape keys
            if a.shapeKey[i] != b.shapeKey[i]: return False
        if a.tangent != None:
            if a.tangent != b.tangent: return False
        return True

class ShapeKeyData:
    def __init__(self, positions, normals, tangents):
        self.positions = positions
        self.normals = normals
        self.tangents = tangents

@functools.total_ordering
class ShapeKeyCompound:
    def __init__(self, position, normal, tangent):
        self.position = position
        self.normal = normal
        self.tangent = tangent

    def __lt__(a, b):
        return a.position < b.position

    def __gt__(a, b):
        return a.position < b.position

    def __eq__(a, b):
        for i in range(3): # compare positions
            if a.position[i] != b.position[i]: return False
        for i in range(3): # compare normals
            if a.normal[i] != b.normal[i]: return False

        return True

class Primitive:
    def __init__(self, uvMapCount = 0, vertexColorCount = 0, shapeKeyCount = 0, boneInfluenceDivisions = 0):
        self.positions = []
        self.normals = []
        self.tangents = []
        self.indices = []
        self.duplicates = {}

        self.uv = []
        for i in range(uvMapCount):
            self.uv.append([])

        self.vertexColor = []
        for i in range(vertexColorCount):
            self.vertexColor.append([])

        self.shapeKey = []
        for i in range(shapeKeyCount):
            self.shapeKey.append(ShapeKeyData([], [], []))

        self.boneID = []
        self.boneInfluence = []
        for i in range(boneInfluenceDivisions):
            self.boneID.append([])
            self.boneInfluence.append([])

    def extend(self, other):
        maxIndex = len(self.positions)
        self.positions.extend(other.positions)
        self.normals.extend(other.normals)
        self.tangents.extend(other.tangents)
        for div, _ in enumerate(self.boneID):
            self.boneID[div].extend(other.boneID[div])
            self.boneInfluence[div].extend(other.boneInfluence[div])

        self.indices.extend([index + maxIndex for index in other.indices])

        for i, uv, in enumerate(self.uv):
            uv.extend(other.uv[i])
        for i, vc, in enumerate(self.vertexColor):
            vc.extend(other.vertexColor[i])

        for i, shape in enumerate(self.shapeKey):
            shape.positions.extend(other.shapeKey[i].positions)
            shape.normals.extend(other.shapeKey[i].normals)
            shape.tangents.extend(other.shapeKey[i].tangents)