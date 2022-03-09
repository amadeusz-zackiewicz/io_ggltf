from io_advanced_gltf2.Keywords import *

def make_object_tracker(objName, library) -> str:
    return objName if library == None else ":".join([library, objName])

def trace_node_id(bucket, objName, library) -> int:
    tracker = make_object_tracker(objName, library)

    if tracker in bucket.trackers[BUCKET_TRACKER_NODES]:
        return bucket.trackers[BUCKET_TRACKER_NODES][tracker]
    else:
        return None

# how to generate tracker id:
#
# mesh id:              <original.name>.<hex(depsgraph_ID).upper>.<mode>|<uv::map::names>|<vertex::color::names>|<shape::key::names>|tangents|<skin (True or False)>
# attribute id:         <original.name>.<hex(depsgraph_ID).upper>.<mode>|<primitive>|<attribute>
#
# if the attribute is not dynamic, for example POSITION or NORMAL, 
# use the attribute type itself, for dynamic attributes such
# as UV maps or weight use the same name as blender
# for example:
# mesh:             cube.0x1234.4|uv_map_final::map_ao|v_color_highlights::shadows::offsets|base::smiling::frowning::suprised|True|True
# mesh, skin only:  cube.0x1234.4|-|-|-|False|True
# attribute:        cube.0x1234.4|0|POSITION or cube.0x1234.0|4|uv_map_final
#
# Q: why the hex()?
# A: looks cooler then pure int

def make_mesh_tracker(meshOriginalName, depsgraphID, mode, uvMaps, vertexColors, shapeKeys, tangents : bool, skin : bool):
    def extend_name(name, l):
        if len(l) > 0:
            name += "|" + "::".join(l)
        else:
            name += "|-"


    name = ".".join([meshOriginalName, str(hex(depsgraphID)).upper(), str(mode)])

    extend_name(name, uvMaps)
    extend_name(name, vertexColors)
    extend_name(name, shapeKeys)

    name += "|" + str(tangents)
    name += "|" + str(skin)

    return name

def trace_mesh_id(bucket, meshOriginalName, depsgraphID, mode, uvMaps, vertexColors, shapeKeys, tangents, skin):

    tracker = make_mesh_tracker(meshOriginalName, depsgraphID, mode, uvMaps, vertexColors, shapeKeys, tangents, skin)

    if tracker in bucket.trackers[BUCKET_TRACKER_MESHES]:
        return bucket.trackers[BUCKET_TRACKER_MESHES][tracker]
    else:
        return None

def make_mesh_attribute_tracker(meshOriginalName, depsgraphID, mode, primitive, attribute):
    """
    The attribute is the variable name for static attributes (such as POSITION or NORMAL)
    blender name for dynamic, for example uv map could be 'uv_map_final'
    """

    name = ".".join([meshOriginalName, str(hex(depsgraphID).upper()), str(mode)])
    name = "|".join([name, str(primitive), attribute])

    return name

def trace_mesh_attribute_id(bucket, meshOriginalName, depsgraphID, mode, primitive, attribute):
    tracker = make_mesh_attribute_tracker(meshOriginalName=meshOriginalName, depsgraphID=depsgraphID, mode=mode, primitive=primitive, attribute=attribute)

    if tracker in bucket.trackers[BUCKET_TRACKER_MESH_ATTRIBUTE]:
        return bucket.trackers[BUCKET_TRACKER_MESH_ATTRIBUTE][tracker]
    else:
        return None