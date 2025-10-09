import bpy
from io_ggltf.Advanced import Settings
from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket as B
from io_ggltf.Core import Writer, ShowFunction
from io_ggltf.Core.Managers import BLStateManager
from warnings import deprecated

@deprecated("Advanced.File.create_bucket is deprecated, it will be removed in future versions and might not function as intended.")
def create_bucket(filePath: str, fileName: str, binPath="/bin", fileType=__c.FILE_TYPE_GLB, targetFrame=0.0):
    """Create a new bucket"""
    depsGraph = bpy.context.evaluated_depsgraph_get()
    bucket = B(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType, dependencyGraph=depsGraph, targetFrame=targetFrame)
    bucket.settings = bucket.settings | Settings.get_default_dict()
    return bucket

@deprecated("Advanced.File.dump_bucket is deprecated, it will be removed in future versions and might not function as intended.")
def dump_bucket(bucket: B):
    """Export the bucket to file. This will delete the bucket"""
    BLStateManager.snapshot_all(bucket)
    Writer.dump_bucket(bucket)

@deprecated("Advanced.File.stage_bucket is deprecated, it will be removed in future versions and might not function as intended.")
def stage_bucket(bucket: B):
    BLStateManager.snapshot_all(bucket)
    Writer.stage_bucket(bucket)

#ShowFunction.Register(create_bucket, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/File-Module#create_bucket")
#ShowFunction.Register(dump_bucket, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/File-Module#dump_bucket")
#ShowFunction.Register(stage_bucket)