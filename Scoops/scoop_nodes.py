import bpy
from mathutils import Quaternion, Vector
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops import scoop_mesh

def __obj_to_node(bucket,
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

    #Util.cleanup_keys(node)
    bucket.trackers[BUCKET_TRACKER_NODES][name] = new_id
    bucket.data[BUCKET_DATA_NODES].append(node)

    return new_id


def scoop_nodes(bucket, names):
    if type(names) != list:
        names = list(names)
    
    for n in names:
        scoop_obj_hierarchy(bucket, bpy.data.objects[n])


def scoop_obj_hierarchy(bucket, obj, local_space = False) -> int:

    children = []
    #children are added first since the parent needs to know their id
    for c in obj.children:
        children.append(scoop_obj_hierarchy(bucket, c, local_space = True))

    if len(children) == 0:
        children = None

    # TODO: if armature, get joints and scoop them

    # if its not a child of something, then we take the world coordinates
    m = obj.matrix_local if local_space else obj.matrix_world
    loc, rot, sc = m.decompose()

    #print("")
    #print(obj.name)
    #print(f"Loc: {loc}")
    #print(f"Rot: {rot}")
    #print(f"Sca: {sc}")
    #print("")

    # auto conversion to Y up if required
    loc = Util.location_ensure_coord_space(bucket, loc)
    rot = Util.rotation_ensure_coord_space(bucket, rot)
    sc = Util.scale_ensure_coord_space(bucket, sc)

    mesh = None

    if obj.type == "MESH":
        mesh = scoop_mesh.scoop_from_obj(bucket, obj)

    # TODO: get mesh, skins, weights

    return __obj_to_node(bucket, 
    name=obj.name, 
    children=children, 
    translation=loc, 
    rotation=rot, 
    scale=sc,
    mesh=mesh
    )