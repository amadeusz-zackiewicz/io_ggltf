from io_advanced_gltf2.Keywords import *
from io_advanced_gltf2.Core.Bucket import Bucket


def is_redundant(bucket: Bucket, obj):
    return id(obj) in bucket.redundancies

def set_predetermined_id(bucket: Bucket, obj, pID):
    bucket.redundancies[id(obj)] = pID

def get_predetermined_id(bucket: Bucket, obj):
    return bucket.redundancies[id(obj)]