from io_ggltf import Constants as __c
from io_ggltf.Core import BlenderUtil, Util

def get_translation(bucket, nodeID: int):
    child, parent = bucket.nodeSpace[nodeID]

    yUp, m = Util.evaluate_matrix(child, parent)
    loc, _, _ = m.decompose()

    if yUp:
        return loc
    else:
        return Util.y_up_location(loc)

def get_rotation(bucket, nodeID: int):
    child, parent = bucket.nodeSpace[nodeID]

    yUp, m = Util.evaluate_matrix(child, parent)
    _, rot, _ = m.decompose()

    if yUp:
        return rot
    else:
        return Util.y_up_rotation(rot)

def get_scale(bucket, nodeID: int):
    child, parent = bucket.nodeSpace[nodeID]

    yUp, m = Util.evaluate_matrix(child, parent)
    _, _, sc = m.decompose()

    if yUp:
        return sc
    else:
        return Util.y_up_scale(sc)

def get_weights(bucket, nodeID: int):
    return None
    #######
    #TODO
    # Data for this is contained in the shape key animation data, check the animated_cube.blend test file.
    # This looks like its going to be a massive pain in the ass to do so im leaving it for later.

def get_custom_property(bucket, nodeID: int, propertyName: str):
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