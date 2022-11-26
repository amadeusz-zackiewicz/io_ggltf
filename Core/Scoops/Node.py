import bpy
from mathutils import Quaternion, Vector
from io_ggltf.Core import Util
from io_ggltf.Constants import *
from io_ggltf.Simple import Mesh
from io_ggltf.Core.Bucket import Bucket

def obj_to_node(
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
        
    node = {}
    if name != None:
        node[NODE_NAME] = name
    else:
        print("No name was given for the node, and a generated one will be used")
        node[NODE_NAME] = str(hex(id(node))).upper()

    if translation != None:
        t = Util.bl_math_to_gltf_list(translation)
        if t[0] == 0.0 and t[1] == 0.0 and t[2] == 0.0:
            pass
        else: 
            node[NODE_TRANSLATION] = t

    if rotation != None:
        r = Util.bl_math_to_gltf_list(rotation)
        if r[0] == 0.0 and r[1] == 0.0 and r[2] == 0.0 and r[3] == 1.0:
            pass
        else:
            node[NODE_ROTATION] = r

    if scale != None:
        s = Util.bl_math_to_gltf_list(scale)
        if s[0] == 1.0 and s[1] == 1.0 and s[2] == 1.0:
            pass
        else:
            node[NODE_SCALE] = s

    if children != None:
        if len(children) > 0:
            node[NODE_CHILDREN] = children

    if mesh != None:
        node[NODE_MESH] = mesh

    if skin != None:
        node[NODE_SKIN] = skin
    
    if weights != None:
        node[NODE_WEIGHTS] = weights

    return node

def make_dummy(bucket: Bucket, assignedID, name):
    bucket.data[BUCKET_DATA_NODES][assignedID] = obj_to_node(name)


def scoop(bucket: Bucket, assignedID, accessor, parent = False):

    obj = Util.try_get_object(accessor)
    bone = Util.try_get_bone(accessor)

    loc, rot, sc = Util.get_yup_transforms(accessor, parent)

    bucket.data[BUCKET_DATA_NODES][assignedID] = obj_to_node(
    name=obj.name if bone == None else bone.name,
    translation=loc,
    rotation=rot,
    scale=sc,
    )
    __record_space(bucket, assignedID, accessor, parent)

def __record_space(bucket, ID, selfAccessor, parentAccessor):
    #print(f"Node space ({ID}): {selfAccessor}, {parentAccessor}")
    bucket.nodeSpace[ID] = (selfAccessor, parentAccessor)
