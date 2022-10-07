import bpy
from io_ggltf.Advanced import Settings
from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket as B
from io_ggltf.Core import Collector, Writer
from io_ggltf.Core.Managers import BLStateManager


def create_bucket(filePath: str, fileName: str, binPath="/bin", fileType=__k.FILE_TYPE_GLB):
    depsGraph = bpy.context.evaluated_depsgraph_get()
    bucket = B(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType, dependencyGraph=depsGraph)
    bucket.settings = bucket.settings | Settings.get_default()
    BLStateManager.snapshot_all(bucket)
    return bucket

def dump_bucket(bucket: B):
    Collector.collect(bucket)
    Writer.dump_bucket(bucket)