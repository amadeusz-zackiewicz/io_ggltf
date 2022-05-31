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
        for i in range(len(a.vColor)): # compare each vertex color
            for vc_i in range(len(a.vColor)):
                if a.vColor[i][vc_i] != b.vColor[i][vc_i]: return False
        for i in range(len(a.shapeKey)): # compare shape keys
            if a.shapeKey[i] != b.shapeKey[i]: return False
        # TODO: tangents are missing
        return True

class ShapeKeyData:
    def __init__(self, positions, normals, tangents):
        self.positions = positions
        self.normals = normals
        self.tangents = tangents

    #def __repr__(self):
        #if len(self.positions) == len(self.normals) and len(self.normals) == len(self.tangents):
            #return "<ShapeKeyData with " + str(len(self.positions)) + " elements>"
        #return "<ShapeKeyData -- " + ", ".join([("Positions: " + str(len(self.positions))), ("Normals: " + str(len(self.normals))), ("Tangents: " + str(len(self.tangents)))]) + ">"

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
        # TODO: tangents and uv are missing
        return True

class Primitive:
    def __init__(self, uvMapCount = 0, vertexColorCount = 0, shapeKeyCount = 0, boneInfluenceDivisions = 0):
        self.positions = []
        self.normals = []
        self.tangents = []
        self.indices = []
        self.duplicates = {}
        self.uv = [[]] * uvMapCount
        self.vertexColor = [[]] * vertexColorCount
        self.shapeKey = [None] * shapeKeyCount
        self.boneID = [[]] * boneInfluenceDivisions
        self.boneInfluence = [[]] * boneInfluenceDivisions
        for i in range(shapeKeyCount):
            self.shapeKey[i] = ShapeKeyData([], [], [])