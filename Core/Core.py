import json
from io_advanced_gltf2.Core.Managers import BufferManager
from io_advanced_gltf2.Core.Util import cleanup_keys
from io_advanced_gltf2.Keywords import *


def bucket_to_file(bucket):
    __to_gltf(bucket)

def __to_gltf(bucket):
    __ensure_scene(bucket)
    BufferManager.write_blobs(bucket)
    cleanup_keys(bucket.data)
    f = open(bucket.settings[BUCKET_SETTING_FILEPATH] + ".gltf", "w")
    _ = json.dump(bucket.data, f, indent=4)
    f.close()

def __ensure_scene(bucket):
    if len(bucket.data[BUCKET_DATA_SCENES]) > 0:
        return
        
    nodes = bucket.data[BUCKET_DATA_NODES]
    top_obj = []
    node_id = []

    scene = {SCENE_NAME : "scene"}

    for n in nodes:
        top_obj.append(True)

    for n in nodes:
        if NODE_CHILDREN in n:
            for c in n[NODE_CHILDREN]:
                top_obj[c] = False

    for i in range(0, len(top_obj)):
        if top_obj[i]:
            node_id.append(i)

    scene[SCENE_NODES] = node_id

    bucket.data[BUCKET_DATA_SCENES].append(scene)
            
