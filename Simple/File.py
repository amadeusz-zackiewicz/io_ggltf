from fileinput import filename
from logging import exception
from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core import Writer
from io_advanced_gltf2.Core.Bucket import Bucket

global __bucket
__bucket = None

def get_current_bucket():
    global __bucket
    return __bucket

def begin(fileName : str, filePath : str, binPath = "bin/", fileType = FILE_TYPE_GLB):
    global __bucket
    if __bucket != None:
        raise Exception("You are trying to being a new file while working on the old one. Please use File.end() before using File.begin()")

    if not filePath.endswith("/"):
        filePath = filePath + "/"
    if not binPath.endswith("/"):
        if binPath != "":
            binPath = binPath + "/"

    __bucket = Bucket(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType)

def end():
    global __bucket
    if __bucket != None:
        Writer.dump_bucket(__bucket)
        __bucket = None
    else:
        raise Exception("Bucket is not initialized, please use File.begin() before using File.end()")