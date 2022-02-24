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

def add(name, blacklist = []):
    global __bucket
    objects = bpy.data.objects
    if name not in objects:
        return
    scoop_nodes.scoop_nodes(__bucket, [name])
    

def end():
    global __bucket
    bucket_to_file(__bucket)
    del __bucket
    pass