from io_ggltf import Constants as __c
from io_ggltf.Core.Bucket import Bucket
from io_ggltf.Core.Blender import NLA, Timeline
import bpy

def snapshot_all(bucket: Bucket):
    Timeline.snapshot_timeline_state(bucket)
    NLA.snapshot_tracks_state(bucket)
