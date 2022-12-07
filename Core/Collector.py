from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Constants import *

def collect(bucket: Bucket):
    #bucket.data[BUCKET_DATA_SCENES] = [None] * bucket.preScoopCounts[BUCKET_DATA_SCENES]
    for dataType in [BUCKET_DATA_SKINS, BUCKET_DATA_MESHES, BUCKET_DATA_NODES]:
        expectedLength = bucket.preScoopCounts[dataType]
        length = len(bucket.data[dataType])
        if length != expectedLength:
            bucket.data[dataType].extend([None for _ in range(expectedLength - length)])

    if len(bucket.nodeSpace) != bucket.preScoopCounts[dataType]:
        bucket.nodeSpace.extend([None for _ in range(bucket.preScoopCounts[BUCKET_DATA_NODES] - len(bucket.nodeSpace))])

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
        for _ in range(0, BUCKET_COMMAND_QUEUE_TYPES):
            bucket.commandQueue.append([])

def __execute_queue(commandQueue: list, inReverse = False):
    if inReverse:
        commandQueue.reverse()

    for c in commandQueue:
        c[0](*c[1])