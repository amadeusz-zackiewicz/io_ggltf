from io_ggltf import Constants as __c
from io_ggltf.Core import BlenderUtil
from io_ggltf.Core.Exceptions import MissingVertexColorsException, MissingShapeKeysException, MissingUVMapsException, MeshComponentValidationFailedException
import bpy 

def validate_mesh(obj):
    if obj == None:
        raise Exception("Mesh Validation: Got 'NoneType', expected a mesh type object")
    elif not object_is_mesh(obj):
        raise Exception(f"Mesh Validation: Got '{obj.type}, expected one of {__c.BLENDER_MESH_CONVERTIBLE} '")

def validate_meshes(objects: list):
    for obj in objects:
        validate_mesh(obj)

def object_is_mesh(obj) -> bool:
    return obj.type in __c.BLENDER_MESH_CONVERTIBLE

def object_has_uv_map(obj, uvMap: str) -> str:
    return uvMap in obj.data.uv_layers

def object_has_uv_maps(obj, uvMaps: list[str]) -> bool:
    for map in uvMaps:
        if not object_has_uv_map(obj, map):
            return False
    return True

def objects_have_uv_maps(objects: list, uvMaps: list[str]):
    for obj in objects:
        for map in uvMaps:
            if not object_has_uv_maps(obj, map):
                return False
    return True

def object_has_vertex_color(obj, vColor: str) -> bool:
    return vColor in obj.data.vertex_colors

def object_has_vertex_colors(obj, vColors: list[str]) -> bool:
    for vc in vColors:
        if not object_has_vertex_color(obj, vc):
            return False
    return True

def objects_have_vertex_colors(objects, vColors: list[str]):
    for obj in objects:
        for vc in vColors:
            if not object_has_vertex_color(obj, vc):
                return False
    return True

def object_has_shape_key(obj, sKey: str) -> bool:
    return sKey in obj.data.shape_keys.key_blocks

def object_has_shape_keys(obj, sKeys: list[str]) -> bool:
    for sk in sKeys:
        if not object_has_shape_key(obj, sk):
            return False
    return True

def objects_have_shape_Keys(objects, sKeys: list[str]):
    for obj in objects:
        for sk in sKeys:
            if not object_has_shape_key(obj, sk):
                return False
    return True

def validate_mesh_component(objects, expectedNames, comparisonMethod, singleComparisonMethod, exceptionType):
    if not comparisonMethod(objects, expectedNames):
        exceptions = []
        for obj in objects:
            missing = []
            for name in expectedNames:
                if not singleComparisonMethod(obj, name):
                    missing.append(name)
            exceptions.append(exceptionType(obj.name, missing))
        for exc in exceptions:
            print(exc)

        if len(exceptions) > 0:
            raise MeshComponentValidationFailedException()

def validate_uv_maps(objects, uvMaps: list[str]):
    validate_mesh_component(
        objects=objects, 
        expectedNames=uvMaps, 
        comparisonMethod=objects_have_uv_maps,
        singleComparisonMethod=object_has_uv_map,
        exceptionType=MissingUVMapsException
        )

def validate_vertex_colors(objects, vColors: list[str]):
    validate_mesh_component(objects=objects,
    expectedNames=vColors,
    comparisonMethod=objects_have_vertex_colors,
    singleComparisonMethod=object_has_vertex_color,
    exceptionType=MissingVertexColorsException
    )

def validate_shape_keys(objects, sKeys: list[str]):
    validate_mesh_component(objects=objects,
    expectedNames=sKeys,
    comparisonMethod=objects_have_shape_Keys,
    singleComparisonMethod=object_has_shape_key,
    exceptionType=MissingShapeKeysException
    )