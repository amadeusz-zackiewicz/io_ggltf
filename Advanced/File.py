import bpy
from io_ggltf.Advanced import Settings
from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket as B
from io_ggltf.Core import Writer
from io_ggltf.Core.Managers import BLStateManager
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/File-Module#create_bucket")
def create_bucket(filePath: str, fileName: str, binPath="/bin", fileType=__c.FILE_TYPE_GLB):
    """Create a new bucket"""
    depsGraph = bpy.context.evaluated_depsgraph_get()
    bucket = B(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType, dependencyGraph=depsGraph)
    bucket.settings = bucket.settings | Settings.get_default_dict()
    BLStateManager.snapshot_all(bucket)
    return bucket

@__ShowInUI(docsURL="https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/File-Module#dump_bucket")
def dump_bucket(bucket: B):
    """Export the bucket to file. This will delete the bucket"""
    Writer.dump_bucket(bucket)

@__ShowInUI()
def stage_bucket(bucket: B):
    Writer.stage_bucket(bucket)
    BLStateManager.snapshot_all(bucket)