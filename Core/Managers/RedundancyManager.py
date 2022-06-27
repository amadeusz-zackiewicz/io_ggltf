from io_advanced_gltf2.Core.Bucket import Bucket
import bpy
from io_advanced_gltf2.Keywords import BUCKET_DATA_NODES

def is_redundant(bucket: Bucket, objGetter: tuple) -> bool:
    return get_eval(bucket.currentDependencyGraph, objGetter) in bucket.redundancies

def add_redundancy(bucket: Bucket, objGetter: tuple, pID):
    bucket.redundancies[get_eval(bucket.currentDependencyGraph, objGetter)] = pID

def get_redundancy(bucket: Bucket, objGetter: tuple) -> int:
    return bucket.redundancies[get_eval(bucket.currentDependencyGraph, objGetter)]

def smart_redundancy(bucket: Bucket, objGetter: tuple, bucketDataType):
    if is_redundant(bucket, objGetter):
        return (True, get_redundancy(bucket, objGetter))
    else:
        newID = bucket.preScoopCounts[bucketDataType]
        bucket.preScoopCounts[bucketDataType] += 1
        add_redundancy(bucket, objGetter, newID)
        return (False, newID)

def get_eval(depsGraph, objGetter: tuple):
    if type(objGetter[0]) == str: # we guess that if the element is a string, then its tuple of (obj.name, obj.library)
        eval = id(depsGraph.id_eval_get(bpy.data.objects.get(objGetter)))
    else:
        eval = tuple([id(depsGraph.id_eval_get(bpy.data.objects.get(o))) for o in objGetter])
    return eval

def reserve_untracked_id(bucket: Bucket, dataType: str):
    oldCount = bucket.preScoopCounts[dataType]
    bucket.preScoopCounts[dataType] += 1
    return oldCount