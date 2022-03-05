import bpy
from io_advanced_gltf2.Scoops import scoop_nodes
from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Core.Core import bucket_to_file

global __bucket
__bucket = None

def begin(file_name: str, folder: str, binaries: str):
    """
    Prepare a bucket that will be used to store objects from your scene.
    """
    global __bucket
    # construct a generic bucket with arguments given
    if not folder.endswith(('/', '//')):
        folder = folder + "/"
    __bucket = Bucket(folder + file_name, binaries)
    pass

def add_selected(blacklist = []):
    """
    Add every selected object and their children to the bucket.
    Optional Parameter:
        blacklist - a list of object names, each object and it's children will not be collected.
    """
    #collect everything that user has selected
    pass

def add_collection(name, blacklist = []):
    #collect the specified collection
    pass

def add(name, library = None, data_types = [], blacklist = []):
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
            scoop_nodes.scoop_hierarchy(__bucket, object, data_types=data_types, blacklist=blacklist)
    

def end():
    global __bucket
    bucket_to_file(__bucket)
    del __bucket
    pass