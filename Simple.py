import bpy
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Scoops import scoop_nodes, scoop_mesh
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core import Writer
from io_advanced_gltf2.Core.Managers import Tracer

global __bucket
__bucket = None

def begin(fileName: str, folder: str, binaries: str, fileType = FILE_TYPE_GLB):
    """
    Prepare a bucket that will be used to store objects from your scene.
    """
    global __bucket
    # construct a generic bucket with arguments given
    if not folder.endswith(('/', '//')):
        folder = folder + "/"
    __bucket = Bucket(folder, fileName, binaries, fileType=fileType)
    pass

def end():
    global __bucket
    Writer.dump_bucket(__bucket)
    del __bucket
    pass

####################################
# Object commands
####################################

def object_add_selected(blacklist = []):
    """
    Add every selected object and their children to the bucket.
    Optional Parameter:
        blacklist - a list of object names, each object and it's children will not be collected.
    """
    #collect everything that user has selected
    pass

def object_add_collection(name, blacklist = []):
    #collect the specified collection
    pass

def object_add(name, library = None, dataTypes = [], blacklist = []):
    global __bucket

    if type(name) != list:
        name = [name]

    for n in name:
        if n in blacklist:
            str_lib = " from library (" + library + ") " if library != None else ""
            print(f"Warning: {n}{str_lib} has been blacklisted and will be omitted")
            continue
        object = bpy.data.objects.get((n, library))
        if object != None:
            scoop_nodes.scoop_hierarchy(__bucket, object, dataTypes=dataTypes, blacklist=blacklist)
    

####################################
# Mesh commands
####################################

def mesh_add_based_on_object(
    objName, 
    library = None, 
    uvMaps = None, 
    vertexColor = None, 
    tangents = False, 
    weights = True, 
    shapeKeys = None
    ):

    global __bucket
    obj = bpy.data.objects.get((objName, library))
    if obj == None:
        lib_str = " from library: " + library if library != None else ""
        print(f"Error: failed to find object with name {objName}{lib_str}")

    return scoop_mesh.scoop_from_obj(__bucket, obj)

def mesh_append_to_node(node_id, mesh_id):
    global __bucket
    node = __bucket.data[BUCKET_DATA_NODES][node_id]
    node[NODE_MESH] = mesh_id

def mesh_append_to_node_hierarchy(objName, mesh_id, library = None, blacklist = []):
    global __bucket

    def recursive_append(obj, mesh_id, blacklist = []):
        global __bucket

        mesh_append_to_node(Tracer.trace_node_id(__bucket, obj.name, library), mesh_id)

        for c in obj.children:
            if c.name not in blacklist:
                recursive_append(c, mesh_id, blacklist)

    obj = bpy.data.objects.get((objName, library))

    if obj == None:
        return

    recursive_append(obj, mesh_id, blacklist)
