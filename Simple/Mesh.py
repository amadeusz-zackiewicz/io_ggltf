from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Simple.File import get_current_bucket
from io_advanced_gltf2.Scoops.Mesh import ScoopMesh
import bpy

def add_based_on_object(objName, 
    normals = False,
    tangents = False, 
    uv = False, 
    vertexColors = False, 
    boneInfluences = False, 
    shapeKeys = False,
    shapeKeyNormals = False,
    shapeKeyTangents = False,
    shapeKeyUV = False
    ):

    obj = bpy.data.objects.get(objName)
    if obj == None:
        lib_str = " from library: " + obj.library if obj.library != None else ""
        print(f"Error: failed to find object with name {lib_str}{objName}")
        return

    uvMapName = []
    vcName = []
    skNames = []

    if uv:
        for uvl in obj.data.uv_layers:
            if uvl.active_render:
                uvMapName.append(uvl.name)

    if vertexColors:
        vcName.append(obj.data.vertex_colors.active.name)

    if shapeKeys:
        for key in obj.data.shape_keys.key_blocks:
            if not key.mute:
                if key.name != "Basis":
                    skNames.append(key.name)

    return ScoopMesh.scoop_from_obj(get_current_bucket(),
    obj, 
    uvMaps=uvMapName,
    vertexColors=vcName,
    shapeKeys=skNames,
    tangents=tangents
    )

def append_to_node(nodeID, meshID):
    node = get_current_bucket().data[BUCKET_DATA_NODES][nodeID]
    node[NODE_MESH] = meshID