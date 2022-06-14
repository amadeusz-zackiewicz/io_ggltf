from io_advanced_gltf2.Core.Bucket import Bucket

def is_redundant(bucket: Bucket, obj) -> bool:
    evalObj = bucket.currentDependencyGraph.id_eval_get(obj)
    return id(evalObj) in bucket.redundancies

def add_redundancy(bucket: Bucket, obj, pID):
    evalObj = bucket.currentDependencyGraph.id_eval_get(obj)
    bucket.redundancies[id(evalObj)] = pID

def get_redundancy(bucket: Bucket, obj) -> int:
    evalObj = bucket.currentDependencyGraph.id_eval_get(obj)
    return bucket.redundancies[id(evalObj)]

def smart_redundancy(bucket: Bucket, obj, bucketDataType):
    if is_redundant(bucket, obj):
        return (True, get_redundancy(bucket, obj))
    else:
        newID = bucket.preScoopCounts[bucketDataType]
        bucket.preScoopCounts[bucketDataType] += 1
        add_redundancy(bucket, obj, newID)
        return (False, newID)