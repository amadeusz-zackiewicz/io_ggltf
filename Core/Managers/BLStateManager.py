from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Blender import NLA
import bpy

def snapshot_all(bucket: Bucket):
    NLA.snapshot_tracks_state(bucket)
