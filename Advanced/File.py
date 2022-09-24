import bpy
from io_ggltf.Advanced import Settings
from io_ggltf import Keywords as __k
from io_ggltf.Core.Bucket import Bucket as B
from io_ggltf.Core import Collector, Writer


def create_bucket(filePath: str, fileName: str, binPath="/bin", fileType=__k.FILE_TYPE_GLB):
    depsGraph = bpy.context.evaluated_depsgraph_get()
    bucket = B(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType, dependencyGraph=depsGraph)
    bucket.settings = bucket.settings | Settings.get_default()
    return bucket

def dump_bucket(bucket: B):
    Collector.collect(bucket)
    Writer.dump_bucket(bucket)