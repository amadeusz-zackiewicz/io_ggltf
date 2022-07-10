from io_advanced_gltf2.Core.Bucket import Bucket
import bpy
from io_advanced_gltf2.Keywords import BUCKET_DATA_NODES

def is_redundant(bucket: Bucket, objGetter: tuple, getFunc = bpy.data.objects.get) -> bool:
    return get_eval(bucket.currentDependencyGraph, objGetter, getFunc) in bucket.redundancies

def add_redundancy(bucket: Bucket, objGetter: tuple, pID: int, getFunc = bpy.data.objects.get):
    bucket.redundancies[get_eval(bucket.currentDependencyGraph, objGetter, getFunc)] = pID

def get_redundancy(bucket: Bucket, objGetter: tuple, getFunc = bpy.data.objects.get) -> int:
    return bucket.redundancies[get_eval(bucket.currentDependencyGraph, objGetter, getFunc)]

def smart_redundancy(bucket: Bucket, objGetter: tuple, bucketDataType: str, getFunc = bpy.data.objects.get):
    if is_redundant(bucket, objGetter, getFunc):
        return (True, get_redundancy(bucket, objGetter, getFunc))
    else:
        newID = bucket.preScoopCounts[bucketDataType]
        bucket.preScoopCounts[bucketDataType] += 1
        add_redundancy(bucket, objGetter, newID, getFunc)
        return (False, newID)

def get_eval(depsGraph, objGetter: tuple, getFunc = bpy.data.objects.get):
    if type(objGetter[0]) == str: # we guess that if the element is a string, then its tuple of (obj.name, obj.library)
        eval = id(depsGraph.id_eval_get(getFunc(objGetter)))
    else:
        eval = tuple([id(depsGraph.id_eval_get(getFunc(o))) for o in objGetter])
    return eval

def reserve_untracked_id(bucket: Bucket, dataType: str):
    oldCount = bucket.preScoopCounts[dataType]
    bucket.preScoopCounts[dataType] += 1
    return oldCount