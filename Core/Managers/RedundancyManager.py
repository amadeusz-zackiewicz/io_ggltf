from io_ggltf.Core.Bucket import Bucket
import bpy
from io_ggltf import Keywords

def __is_not_unique(bucket: Bucket, objAccessor, getFunc = bpy.data.objects.get) -> bool:
    return __get_eval(bucket.currentDependencyGraph, objAccessor, getFunc) in bucket.redundancies

def __add_unique(bucket: Bucket, objAccessor, pID: int, getFunc = bpy.data.objects.get):
    bucket.redundancies[__get_eval(bucket.currentDependencyGraph, objAccessor, getFunc)] = pID

def fetch_unique(bucket: Bucket, objAccessor, getFunc = bpy.data.objects.get) -> int:
    return bucket.redundancies[__get_eval(bucket.currentDependencyGraph, objAccessor, getFunc)]

def register_unique(bucket: Bucket, objAccessor, bucketDataType: str, getFunc = bpy.data.objects.get):
    if __is_not_unique(bucket, objAccessor, getFunc):
        return (True, fetch_unique(bucket, objAccessor, getFunc))
    else:
        newID = bucket.preScoopCounts[bucketDataType]
        bucket.preScoopCounts[bucketDataType] += 1
        __add_accessor(bucket, objAccessor, bucketDataType, newID)
        __add_unique(bucket, objAccessor, newID, getFunc)
        return (False, newID)

def __get_eval(depsGraph, objAccessor, getFunc = bpy.data.objects.get):
    if type(objAccessor) == list:
        eval = tuple([id(depsGraph.id_eval_get(getFunc(o))) for o in objAccessor])
    elif type(objAccessor) == str:
        eval = id(depsGraph.id_eval_get(getFunc(objAccessor)))
    elif type(objAccessor) == tuple:
        if len(objAccessor) == 3: ## if the accessor has 3 elements, then its a bone, we assume that the getFunc is getting an object
            eval = id(depsGraph.id_eval_get(getFunc((objAccessor[0], objAccessor[1])).pose.bones[objAccessor[2]]))
        else:
            eval = id(depsGraph.id_eval_get(getFunc(objAccessor)))
    else:
        raise Exception(f"Invalid accessor type, expected string, tuple or list, got: {type(objAccessor)}")
    return eval

def register_unsafe(bucket: Bucket, accessor, dataType: str):
    oldCount = bucket.preScoopCounts[dataType]
    __add_accessor(bucket, accessor, dataType, oldCount) 
    bucket.preScoopCounts[dataType] += 1
    return oldCount

def __add_accessor(bucket, accessor, dataType, id):
    if type(accessor) == list:
        accessor = tuple(accessor)
    elif type(accessor) == str:
        accessor = (accessor, None)

    if accessor in bucket.accessors[dataType]:
        if type(bucket.accessors[dataType][accessor]) != list:
            bucket.accessors[dataType][accessor] = [bucket.accessors[dataType][accessor], id]
        else:
            bucket.accessors[dataType][accessor].append(id)
    else:
        bucket.accessors[dataType][accessor] = id

def fetch_id_from_unsafe(bucket, accessor, dataType) -> int or list[int]:
    if type(accessor) == list:
        accessor = tuple(accessor)
    elif type(accessor) == str:
        accessor = (accessor, None)
        
    if accessor in bucket.accessors[dataType]:
        return bucket.accessors[dataType][accessor]
    else:
        raise Exception(f"{accessor} has no assigned ID, please make sure you add the desired object to the bucket first.")

def fetch_first_id_from_unsafe(bucket, accessor, dataType) -> int:
    if type(accessor) == list:
        accessor = tuple(accessor)
    elif type(accessor) == str:
        accessor = (accessor, None)

    if accessor in bucket.accessors[dataType]:
        id = bucket.accessors[dataType][accessor]
        if type(id) == list:
            return id[0]
        else:
            return id
    else:
        raise Exception(f"{accessor} has no assigned ID, please make sure you add the desired object to the bucket first.")

def fetch_last_id_from_unsafe(bucket, accessor, dataType) -> int:
    if type(accessor) == list:
        accessor = tuple(accessor)
    elif type(accessor) == str:
        accessor = (accessor, None)

    if accessor in bucket.accessors[dataType]:
        id = bucket.accessors[dataType][accessor]
        if type(id) == list:
            return id[-1]
        else:
            return id
    else:
        raise Exception(f"{accessor} ({dataType}) has no assigned ID, please make sure you add the desired object to the bucket first.")