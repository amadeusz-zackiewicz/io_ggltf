from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Constants import *

def collect(bucket: Bucket):
    #bucket.data[BUCKET_DATA_SCENES] = [None] * bucket.preScoopCounts[BUCKET_DATA_SCENES]
    bucket.data[BUCKET_DATA_SKINS] = [None] * bucket.preScoopCounts[BUCKET_DATA_SKINS]
    bucket.data[BUCKET_DATA_MESHES] = [None] * bucket.preScoopCounts[BUCKET_DATA_MESHES]
    bucket.data[BUCKET_DATA_NODES] = [None] * bucket.preScoopCounts[BUCKET_DATA_NODES]
    bucket.nodeSpace = [None] * bucket.preScoopCounts[BUCKET_DATA_NODES]
    try:
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_SETUP])
        bucket.currentDependencyGraph.update()
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_SKIN])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_MESH])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_NODE])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_LINKER])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_ANIM_SETUP])
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_NAMING])
    except Exception as e:
        print("Encountered exception during command execution:",e)
        raise Exception("Export was aborted due to an exception being encountered, check above for details.")
    finally:
        __execute_queue(bucket.commandQueue[COMMAND_QUEUE_CLEAN_UP], True)
        bucket.currentDependencyGraph.update()
        del bucket.commandQueue
        bucket.commandQueue = []
        for i in range(0, BUCKET_COMMAND_QUEUE_TYPES):
            bucket.commandQueue.append([])

def __execute_queue(commandQueue: list, inReverse = False):
    if inReverse:
        commandQueue.reverse()

    for c in commandQueue:
        c[0](*c[1])