import bpy
from io_advanced_gltf2.Advanced import Settings
from io_advanced_gltf2.Keywords import FILE_TYPE_GLTF_EMBEDDED
from io_advanced_gltf2.Core.Bucket import Bucket as B
from io_advanced_gltf2.Core import Collector, Writer


def create_bucket(filePath: str, fileName: str, binPath="/bin", fileType=FILE_TYPE_GLTF_EMBEDDED):
    depsGraph = bpy.context.evaluated_depsgraph_get()
    bucket = B(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType, dependencyGraph=depsGraph)
    bucket.settings = bucket.settings | Settings.get_default()
    return bucket

def dump_bucket(bucket: B):
    Collector.collect(bucket)
    Writer.dump_bucket(bucket)