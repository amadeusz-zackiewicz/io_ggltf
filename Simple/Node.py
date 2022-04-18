from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Util
from io_advanced_gltf2.Simple.File import get_current_bucket
from io_advanced_gltf2.Scoops import Node
import bpy

def make_new(name: str, position, rotation, scale, convertToYup = False):
    bucket = get_current_bucket()
    if convertToYup:
        position = Util.location_ensure_coord_space(position)
        rotation = Util.rotation_ensure_coord_space(rotation)
        scale = Util.scale_ensure_coord_space(scale)

    node = {
        NODE_NAME: name,
        NODE_TRANSLATION: position,
        NODE_ROTATION: rotation,
        NODE_SCALE: scale
    }

    nodeID = len(bucket.data[BUCKET_DATA_NODES])
    bucket.data[BUCKET_DATA_NODES].append(node)

    return nodeID

def add_based_on_object(objName, includeData = True, useLocalSpace = False):

    obj = bpy.data.objects.get(objName)
    if obj == None:
        raise Exception(f"{objName} not found within blend data, please double check your spelling and library")

    return Node.scoop_object(get_current_bucket(), obj, includeData, useLocalSpace)

def add_object_hierarchy(objName, includeData = True, useLocalSpace = False, blacklist = []):

    obj = bpy.data.objects.get(objName)
    if obj != None:
        Node.scoop_hierarchy(get_current_bucket(), 
        obj, 
        includeData=includeData,
        useLocalSpace=useLocalSpace, 
        blacklist=blacklist
        )