import bpy
from mathutils import Quaternion, Vector
from io_ggltf.Core import Util
from io_ggltf.Keywords import *
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

    return node

def scoop_object(bucket: Bucket, assignedID, objAccessor, parent = False):

    obj = bpy.data.objects.get(objAccessor)

    correctedMatrix = False
    if parent == False:
        m = obj.matrix_world
    elif parent == True:
        m = obj.matrix_local
    else: # we assume that this is an accessor
        parentObj = Util.try_get_object(parent)
        try:
            bone = Util.try_get_bone(parent)
        except:
            bone = None

        if bone != None:
            correctedMatrix = True
            pMatrix = parentObj.matrix_world @ bone.matrix
            m = pMatrix.inverted_safe() @ obj.matrix_world
            m @= Util.get_basis_matrix_conversion().inverted_safe()
            # This looks wrong, but it produces the correct result, good enough for now
        else:
            m = parentObj.matrix_world.inverted_safe() @ obj.matrix_world

    if correctedMatrix:
        loc, rot, sc = m.decompose()
    else:
        loc, rot, sc = m.decompose()
        loc = Util.y_up_location(loc)
        rot = Util.y_up_rotation(rot)
        sc = Util.y_up_scale(sc)
        

    bucket.data[BUCKET_DATA_NODES][assignedID] = obj_to_node(
    name=obj.name,
    translation=loc,
    rotation=rot,
    scale=sc,
    )

# def __include_data(bucket, obj):
#     mesh = None
#     skin = None
#     weights = None

#     if obj.type in BLENDER_MESH_CONVERTIBLE:
#             if obj.type == BLENDER_TYPE_MESH:
#                 normals = bucket.settings[BUCKET_SETTING_MESH_GET_NORMALS]
#                 tangents = bucket.settings[BUCKET_SETTING_MESH_GET_TANGENTS]
#                 getSkin = bucket.settings[BUCKET_SETTING_MESH_GET_BONE_INFLUENCE]
#                 uvs = bucket.settings[BUCKET_SETTING_MESH_GET_UVS]
#                 vColors = bucket.settings[BUCKET_SETTING_MESH_GET_VERTEX_COLORS]
#                 sk = bucket.settings[BUCKET_SETTING_MESH_GET_SHAPE_KEYS]
                

#                 mesh, skin, weights = Mesh.add_based_on_object((obj.name, obj.library),
#                 normals=normals,
#                 tangents=tangents, 
#                 uv=uvs, 
#                 boneInfluences=getSkin,
#                 boneGetInverseBinds=getSkin,
#                 shapeKeys=sk, 
#                 vertexColors=vColors)
    
#     return (mesh, skin, weights)
