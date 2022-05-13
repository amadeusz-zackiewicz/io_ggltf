from io_advanced_gltf2.Core.Bucket import Bucket


def is_redundant(bucket: Bucket, obj):
    evalObj = bucket.currentDependencyGraph.id_eval_get(obj)
    return id(evalObj) in bucket.redundancies

def add_redundancy(bucket: Bucket, obj, pID):
    evalObj = bucket.currentDependencyGraph.id_eval_get(obj)
    bucket.redundancies[id(evalObj)] = pID

def get_redundancy(bucket: Bucket, obj):
    evalObj = bucket.currentDependencyGraph.id_eval_get(obj)
    return bucket.redundancies[id(evalObj)]

def auto_redundancy(bucket: Bucket, obj, bucketDataType):
    if is_redundant(bucket, obj):
        return (True, get_redundancy(bucket, obj))
    else:
        newID = len(bucket.preScoopCounts[bucketDataType])
        bucket.preScoopCounts[bucketDataType]
        add_redundancy(bucket, obj, newID)
        return (False, newID)