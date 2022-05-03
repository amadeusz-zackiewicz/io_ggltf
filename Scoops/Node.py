import bpy
from mathutils import Quaternion, Vector
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Simple import Mesh
from io_advanced_gltf2.Core.Managers import Tracer

def __obj_to_node(bucket,
    tracker=None,
    name = None,
    translation = None,
    rotation = None,
    scale = None,
    children = None,
    camera = None,
    mesh = None,
    skin = None,
    weights = None,
    extensions = None,
    extras = None
):

    if name == None:
        print("could not read the name of the object")
        name = ""

    new_id = len(bucket.data[BUCKET_DATA_NODES])
    node = {}
    if name != None:
        node[NODE_NAME] = name
    else:
        print("No name was given for the node, and a generated one will be used")
        node[NODE_NAME] = str(hex(id(node))).upper()

    if translation != None:
        node[NODE_TRANSLATION] = Util.bl_math_to_gltf_list(translation)

    if rotation != None:
        node[NODE_ROTATION] = Util.bl_math_to_gltf_list(rotation)

    if scale != None:
        node[NODE_SCALE] = Util.bl_math_to_gltf_list(scale)

    if children != None:
        if len(children) > 0:
            node[NODE_CHILDREN] = children

    if mesh != None:
        node[NODE_MESH] = mesh

    if skin != None:
        node[NODE_SKIN] = skin
    
    if weights != None:
        node[NODE_WEIGHTS] = weights

    if tracker != None:
        bucket.trackers[BUCKET_TRACKER_NODES][tracker] = new_id
    bucket.data[BUCKET_DATA_NODES].append(node)

    return new_id


def scoop_hierarchy(bucket, obj, includeData, useLocalSpace, blacklist = []):
        __scoop_hierarchy(bucket, obj, includeData=includeData, localSpace=useLocalSpace, blacklist=blacklist)


def __scoop_hierarchy(bucket, obj, includeData, blacklist = [], localSpace = False) -> int:

    children = []
    #children are added first since the parent needs to know their id
    for c in obj.children:
        if c.name not in blacklist:
            children.append(__scoop_hierarchy(bucket, c, includeData=includeData, blacklist = blacklist, localSpace = True))

    if len(children) == 0:
        children = None

    # TODO: if armature, get joints and scoop them

    # if its not a child of something, then we take the world coordinates
    m = obj.matrix_local if localSpace else obj.matrix_world
    loc, rot, sc = m.decompose()

    # auto conversion to Y up if required
    loc = Util.y_up_location(loc)
    rot = Util.y_up_rotation(rot)
    sc = Util.y_up_scale(sc)

    mesh = None
    skin = None
    weights = None

    if includeData:
        mesh, skin , weights = __include_data(bucket, obj)

    tracker = Tracer.make_object_tracker(obj.name, obj.library, localSpace)

    return __obj_to_node(bucket,
    tracker=tracker, 
    name=obj.name, 
    children=children, 
    translation=loc, 
    rotation=rot, 
    scale=sc,
    mesh=mesh,
    skin=skin,
    weights=weights
    )

def scoop_object(bucket, obj, includeData, localSpace = False):

    node_id = Tracer.trace_node_id(bucket, obj.name, obj.library, localSpace)
    if node_id != None:
        return node_id

    m = obj.matrix_local if localSpace else obj.matrix_world
    loc, rot, sc = m.decompose()

    loc = Util.y_up_location(loc)
    rot = Util.y_up_rotation(rot)
    sc = Util.y_up_scale(sc)

    mesh = None
    skin = None
    weights = None

    if includeData:
        mesh, skin, weights = __include_data(bucket, obj)

    tracker = Tracer.make_object_tracker(obj.name, obj.library, localSpace)

    return __obj_to_node(bucket,
    tracker=tracker,
    name=obj.name,
    translation=loc,
    rotation=rot,
    scale=sc,
    mesh=mesh,
    skin=skin,
    weights=weights
    )

def __include_data(bucket, obj):
    mesh = None
    weights = None

    if obj.type in BLENDER_MESH_CONVERTIBLE:
            if obj.type == BLENDER_TYPE_MESH:
                normals = bucket.settings[BUCKET_SETTING_MESH_GET_NORMALS]
                tangents = bucket.settings[BUCKET_SETTING_MESH_GET_TANGENTS]
                skin = bucket.settings[BUCKET_SETTING_MESH_GET_SKIN]
                uvs = []
                vColors = []
                sk = []
                if bucket.settings[BUCKET_SETTING_MESH_GET_UVS]:
                    for uv in obj.data.uv_layers:
                        if uv.active_render:
                            uvs.append(uv.name)
                if bucket.settings[BUCKET_SETTING_MESH_GET_VERTEX_COLORS]:
                    vColors.append(obj.data.vertex_colors.active.name)
                if bucket.settings[BUCKET_SETTING_MESH_GET_SHAPE_KEYS]:
                    for key in obj.data.shape_keys.key_blocks:
                        if not key.mute:
                            if key.name != "Basis":
                                sk.append(key.name)

                mesh, skin, weights = Mesh.add_based_on_object((obj.name, obj.library),tangents=tangents, uvMaps=uvs, skin=skin, shapeKeys=sk, vertexColors=vColors)
    
    return (mesh, skin, weights)
