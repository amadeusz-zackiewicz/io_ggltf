from io_ggltf import Constants as __c
from io_ggltf.Core import BlenderUtil, Util

def get_translation(bucket, nodeID: int):
    loc, _, _ = Util.get_yup_transforms(*bucket.nodeSpace[nodeID])
    return loc

def get_rotation(bucket, nodeID: int):
    _, rot, _ = Util.get_yup_transforms(*bucket.nodeSpace[nodeID])
    return rot

def get_scale(bucket, nodeID: int):
    _, _, sc = Util.get_yup_transforms(*bucket.nodeSpace[nodeID])
    return sc

def get_weights(bucket, nodeID: int):
    return None
    #######
    #TODO
    # Data for this is contained in the shape key animation data, check the animated_cube.blend test file.
    # This looks like its going to be a massive pain in the ass to do so im leaving it for later.

def get_custom_property(bucket, nodeID: int, propertyName: str):
    # according to the gltf spec, custom properties are not supported at all
    # which might mean that they will be ignored by importing softwares 
    # unless user has control over import process (or there is an extension)
    obj = Util.try_get_object(bucket.basis[nodeID])
    bone = Util.try_get_bone(bucket.basis[nodeID])

    if bone != None:
        obj = bone
    try:
        return obj.__getattribute__(propertyName)
    except:
        return None

__defaultProperties = {
    __c.NODE_TRANSLATION: get_translation,
    __c.NODE_ROTATION: get_rotation,
    __c.NODE_SCALE: get_scale,
    __c.NODE_WEIGHTS: get_weights
}

def is_default_property(propertyName: str) -> bool:
    return propertyName in __defaultProperties

def get_default_property(bucket, nodeID: int, propertyName: str):
    return __defaultProperties[propertyName](bucket, nodeID)

def get_property(bucket, nodeID: int, propertyName: str):
    if is_default_property(propertyName):
        return get_default_property(bucket, nodeID, propertyName)
    else:
        return get_custom_property(bucket, nodeID, propertyName)