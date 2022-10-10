# from fileinput import filename
# from logging import exception
# from io_ggltf.Constants import *
# from io_ggltf.Core import Writer
# from io_ggltf.Core.Bucket import Bucket

# global __bucket
# __bucket = None

# def get_current_bucket():
#     global __bucket
#     return __bucket

# def init(fileName : str, filePath : str, binPath = "bin/", fileType = FILE_TYPE_GLB):
#     global __bucket
#     if __bucket != None:
#         raise Exception("You are trying to being a new file while working on the old one. Please use File.end() before using File.begin()")

#     if not filePath.endswith("/"):
#         filePath = filePath + "/"
#     if not binPath.endswith("/"):
#         if binPath != "":
#             binPath = binPath + "/"

#     __bucket = Bucket(filePath=filePath, fileName=fileName, binPath=binPath, fileType=fileType)
    
# def set_setting(setting: str, value: any):
#     global __bucket
    
#     if __bucket == None:
#         raise Exception("Please use File.init() before changing any settings")
    
#     __bucket.settings[setting] = value
    
# def is_setting_set(setting: str) -> bool:
#     global __bucket
    
#     if __bucket == None:
#         raise Exception("Please use File.init() before checking for settings")
    
#     return setting in __bucket.settings
    
# def begin():
#     pass

# def end():
#     global __bucket
#     if __bucket != None:
#         Writer.dump_bucket(__bucket)
#         __bucket = None
#     else:
#         raise Exception("Bucket is not initialized, please use File.init() before using File.end()")