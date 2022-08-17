from io_ggltf.Core.Bucket import Bucket
import bpy
from io_ggltf.Keywords import BUCKET_DATA_NODES

def is_redundant(bucket: Bucket, objAccessor: tuple, getFunc = bpy.data.objects.get) -> bool:
    return get_eval(bucket.currentDependencyGraph, objAccessor, getFunc) in bucket.redundancies

def add_redundancy(bucket: Bucket, objAccessor: tuple, pID: int, getFunc = bpy.data.objects.get):
    bucket.redundancies[get_eval(bucket.currentDependencyGraph, objAccessor, getFunc)] = pID

def get_redundancy(bucket: Bucket, objAccessor: tuple, getFunc = bpy.data.objects.get) -> int:
    return bucket.redundancies[get_eval(bucket.currentDependencyGraph, objAccessor, getFunc)]

def smart_redundancy(bucket: Bucket, objAccessor: tuple, bucketDataType: str, getFunc = bpy.data.objects.get):
    if is_redundant(bucket, objAccessor, getFunc):
        return (True, get_redundancy(bucket, objAccessor, getFunc))
    else:
        newID = bucket.preScoopCounts[bucketDataType]
        bucket.preScoopCounts[bucketDataType] += 1
        add_redundancy(bucket, objAccessor, newID, getFunc)
        return (False, newID)

def get_eval(depsGraph, objAccessor: tuple, getFunc = bpy.data.objects.get):
    if type(objAccessor[0]) == str: # we guess that if the element is a string, then its tuple of (obj.name, obj.library)
        eval = id(depsGraph.id_eval_get(getFunc(objAccessor)))
    else:
        eval = tuple([id(depsGraph.id_eval_get(getFunc(o))) for o in objAccessor])
    return eval

def reserve_untracked_id(bucket: Bucket, dataType: str):
    oldCount = bucket.preScoopCounts[dataType]
    bucket.preScoopCounts[dataType] += 1
    return oldCount