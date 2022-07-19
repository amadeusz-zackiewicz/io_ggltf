from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Managers import RedundancyManager as RM
import bpy

def based_on_object(bucket: Bucket, objAccessor,
normals=False,
tangents=False,
uvMaps=[],
vertexColors=[],
boneInfluences=False,
skinID=None,
shapeKeys=False,
shapeKeyNormals=False,
shapeKeyTangents=False,
shapeKeyUVs=False
) -> int:

    obj = bpy.data.objects.get(objAccessor)
    if obj == None:
        return None

    