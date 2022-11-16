from io_ggltf.Core.Bucket import Bucket
import bpy
from io_ggltf import Constants

def __is_duplicate(bucket: Bucket, objAccessor, useData: bool) -> bool:
    """Does this entry exist?"""
    return __get_eval(bucket.currentDependencyGraph, objAccessor, useData=useData) in bucket.redundancies

def __add_unique(bucket: Bucket, objAccessor, pID: int, useData: bool):
    bucket.redundancies[__get_eval(bucket.currentDependencyGraph, objAccessor, useData=useData)] = pID

def fetch_unique(bucket: Bucket, objAccessor, useData: bool) -> int:
    eval = __get_eval(bucket.currentDependencyGraph, objAccessor, useData=useData)
    if eval in bucket.redundancies:
        return bucket.redundancies[eval]
    else:
        return None

def __should_use_data(dataType: str) -> bool:
    return dataType in Constants.REDUNDANCY_USE_DATA

def register_unique(bucket: Bucket, objAccessor, bucketDataType: str):
    """Register a unique entry
    
    Returns: tuple[bool, id] where bool indicates whether entry already exists.
    """
    useData = __should_use_data(bucketDataType)
    if __is_duplicate(bucket, objAccessor, useData):
        return (True, fetch_unique(bucket, objAccessor, useData))
    else:
        newID = bucket.preScoopCounts[bucketDataType]
        bucket.preScoopCounts[bucketDataType] += 1
        __add_accessor(bucket, objAccessor, bucketDataType, newID)
        __add_unique(bucket, objAccessor, newID, useData)
        return (False, newID)

def __get_eval(depsGraph, objAccessor, useData: bool):
    if type(objAccessor) == list:
        if useData:
            eval = tuple([id(bpy.data.objects.get(o).evaluated_get(depsGraph).data for o in objAccessor)])
        else:
            eval = tuple([id(bpy.data.objects.get(o).evaluated_get(depsGraph) for o in objAccessor)])
    elif type(objAccessor) == str:
        if useData:
            eval = id(bpy.data.objects.get(objAccessor).evaluated_get(depsGraph).data)
        else:
            eval = id(bpy.data.objects.get(objAccessor).evaluated_get(depsGraph))
    elif type(objAccessor) == tuple:
        if len(objAccessor) == 3: ## if the accessor has 3 elements, then its a bone
            eval = id(bpy.data.objects.get((objAccessor[0], objAccessor[1])).pose.bones[objAccessor[2]].evaluated_get(depsGraph))
        else:
            if useData:
                eval = id(bpy.data.objects.get(objAccessor).evaluated_get(depsGraph).data)
            else:
                eval = id(bpy.data.objects.get(objAccessor).evaluated_get(depsGraph))
    else:
        raise Exception(f"Invalid accessor type, expected string, tuple or list, got: {type(objAccessor)}")
    #print(objAccessor, "Eval:", eval, "data:", useData)
    return eval

def register_unsafe(bucket: Bucket, accessor, dataType: str):
    """Register new entry with possible duplicates"""
    oldCount = bucket.preScoopCounts[dataType]
    __add_accessor(bucket, accessor, dataType, oldCount) 
    bucket.preScoopCounts[dataType] += 1
    return oldCount

def __add_accessor(bucket, accessor, dataType, id: int):
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

def register_dummy(bucket:Bucket, dataType: str):
    oldCount = bucket.preScoopCounts[dataType]
    bucket.preScoopCounts[dataType] += 1
    return oldCount