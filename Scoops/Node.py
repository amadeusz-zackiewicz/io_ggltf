import bpy
from mathutils import Quaternion, Vector
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops.Mesh import ScoopMesh
from io_advanced_gltf2.Core.Managers import Tracer

def __obj_to_node(bucket,
    tracker,
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
    node[NODE_NAME] = name

    if translation != None:
        node[NODE_TRANSLATION] = Util.bl_math_to_gltf_list(translation)
    else:
        node[NODE_TRANSLATION] = [0.0, 0.0, 0.0]
        print(f"Failed to get location for object {name} defaulting to 0, 0, 0")

    if rotation != None:
        node[NODE_ROTATION] = Util.bl_math_to_gltf_list(rotation)
    else:
        node[NODE_ROTATION] = Util.bl_math_to_gltf_list(Util.rotation_ensure_coord_space(bucket, Quaternion.identity()))
        print(f"Failed to get rotation for object {name} defaulting to 0, 0, 0")

    if scale != None:
        node[NODE_SCALE] = Util.bl_math_to_gltf_list(scale)
    else:
        node[NODE_SCALE] = [1.0, 1.0, 1.0]
        print(f"Failed to get scale for object {name} defaulting to 1, 1, 1")

    if children != None:
        node[NODE_CHILDREN] = children

    if mesh != None:
        node[NODE_MESH] = mesh

    bucket.trackers[BUCKET_TRACKER_NODES][tracker] = new_id
    bucket.data[BUCKET_DATA_NODES].append(node)

    return new_id


def scoop_hierarchy(bucket, objs, dataTypes = [], blacklist = []):
    if type(objs) != list:
        objs = [objs]
    
    for o in objs:
        __scoop_hierarchy(bucket, o, dataTypes=dataTypes, blacklist=blacklist)


def __scoop_hierarchy(bucket, obj, dataTypes = [], blacklist = [], localSpace = False) -> int:

    children = []
    #children are added first since the parent needs to know their id
    for c in obj.children:
        if c.name not in blacklist:
            children.append(__scoop_hierarchy(bucket, c, blacklist = blacklist, localSpace = True))

    if len(children) == 0:
        children = None

    # TODO: if armature, get joints and scoop them

    # if its not a child of something, then we take the world coordinates
    m = obj.matrix_local if localSpace else obj.matrix_world
    loc, rot, sc = m.decompose()

    # auto conversion to Y up if required
    loc = Util.location_ensure_coord_space(loc)
    rot = Util.rotation_ensure_coord_space(rot)
    sc = Util.scale_ensure_coord_space(sc)

    mesh = None

    if obj.type == BLENDER_TYPE_MESH and BLENDER_TYPE_MESH in dataTypes:
        mesh = ScoopMesh.scoop_from_obj(bucket, obj)

    # TODO: skins, weights

    tracker = Tracer.make_object_tracker(obj.name, obj.library)

    return __obj_to_node(bucket,
    tracker=tracker, 
    name=obj.name, 
    children=children, 
    translation=loc, 
    rotation=rot, 
    scale=sc,
    mesh=mesh
    )