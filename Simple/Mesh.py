from io_ggltf.Constants import *
from io_ggltf.Simple.File import get_current_bucket
from io_ggltf.Core.Scoops.Mesh import ScoopMesh
from io_ggltf.Simple import Skin
import bpy
from io_ggltf.Core.Bucket import Bucket

def add_based_on_object(objAccessor, 
    normals = False,
    tangents = False, 
    uv = False, 
    vertexColors = False, 
    boneInfluences = False,
    boneForceRestPose = False,
    boneGetInverseBinds = False,
    boneBlacklist = [],
    shapeKeys = False,
    shapeKeyNormals = False,
    shapeKeyTangents = False,
    shapeKeyUV = False
    ):

    bucket = get_current_bucket()
    depsGraph = bucket.currentDependencyGraph

    obj = bpy.data.objects.get(objAccessor)
    if obj == None:
        lib_str = " from library: " + obj.library if obj.library != None else ""
        print(f"Error: failed to find object with name {lib_str}{objAccessor}")
        return

    modifierReset = []
    uvMapName = []
    vcName = []
    skNames = []
    skinID = None

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

    if boneInfluences:
        for i, mod in enumerate(obj.modifiers):
            if mod.type == BLENDER_MODIFIER_ARMATURE:
                if skinID == None:
                    skinID = Skin.add_based_on_object((mod.object.name, mod.object.library), boneGetInverseBinds, boneForceRestPose, boneBlacklist)
                if depsGraph.mode == BLENDER_DEPSGRAPH_MODE_VIEWPORT:
                    modifierReset.append(mod.show_viewport)
                    mod.show_viewport = False
                else:
                    modifierReset.append(mod.show_render)
                    mod.show_render = False
            else:
                modifierReset.append(None)
                
        depsGraph.update()
        obj = bpy.data.objects.get(objAccessor) # get the reference again in case it became invalid


    meshID, weights = ScoopMesh.scoop_from_obj(bucket,
    obj,
    normals=normals,
    uvMaps=uvMapName,
    vertexColors=vcName,
    shapeKeys=skNames,
    tangents=tangents,
    skinID=skinID
    )

    if boneInfluences:
        for i, mod in enumerate(obj.modifiers):
            if modifierReset[i] != None:
                if depsGraph.mode == BLENDER_DEPSGRAPH_MODE_VIEWPORT:
                    mod.show_viewport = modifierReset[i]
                else:
                    mod.show_render = modifierReset[i]
        depsGraph.update()

    return (meshID, skinID, weights)

def append_to_node(nodeID, meshID):
    node = get_current_bucket().data[BUCKET_DATA_NODES][nodeID]
    node[NODE_MESH] = meshID

def append_to_node_hierarchy(nodeID, meshID, blacklist = []):

    node = get_current_bucket().data[BUCKET_DATA_NODES][nodeID]

    if node[NODE_NAME] in blacklist:
        return

    node[NODE_MESH] = meshID
    if NODE_CHILDREN in node.keys():
        for cID in node[NODE_CHILDREN]:
            append_to_node_hierarchy(cID, meshID, blacklist)