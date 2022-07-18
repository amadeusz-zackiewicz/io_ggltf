from io_advanced_gltf2.Core.Bucket import Bucket
from io_advanced_gltf2.Keywords import *

def collect(bucket: Bucket):
    bucket.data[BUCKET_DATA_SCENES] = [None] * bucket.preScoopCounts[BUCKET_DATA_SCENES]
    bucket.data[BUCKET_DATA_SKINS] = [None] * bucket.preScoopCounts[BUCKET_DATA_SKINS]
    bucket.skinDefinition = [None] * bucket.preScoopCounts[BUCKET_DATA_SKINS]
    bucket.data[BUCKET_DATA_MESHES] = [None] * bucket.preScoopCounts[BUCKET_DATA_MESHES]
    bucket.data[BUCKET_DATA_NODES] = [None] * bucket.preScoopCounts[BUCKET_DATA_NODES]
    try:
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_SETUP])
        bucket.currentDependencyGraph.update()
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_SKIN])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_MESH])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_NODE])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_LINKER])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_ANIM_SETUP])
        bucket.currentDependencyGraph.update()
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP], True)
        bucket.currentDependencyGraph.update()
    except Exception as e:
        print("Encountered exception during command execution:",e)
        del bucket
        raise Exception("Export was aborted due to an exception being encountered, check above for details.")

def __execute_queue(commandQueue: list, inReverse = False):
    for c in commandQueue:
        c[0](*c[1])