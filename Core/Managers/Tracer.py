from io_advanced_gltf2.Keywords import *

def make_object_tracker(objName, library) -> str:
    return objName if library == None else ":".join([library, objName])

def trace_node_id(bucket, objName, library) -> int:
    tracker = make_object_tracker(objName, library)

    if tracker in bucket.trackers[BUCKET_TRACKER_NODES]:
        return bucket.trackers[BUCKET_TRACKER_NODES][tracker]
    else:
        return None
