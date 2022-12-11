import bpy
from io_ggltf import Constants as __c

def set_frame(frame: float):
    bpy.context.scene.frame_float = frame

def get_current_frame():
    return bpy.context.scene.frame_float

def is_frame_step_valid(frameStart: float, frameEnd: float, frameStep: float):
    return (frameEnd - frameStart) % frameStep == 0.0

def snapshot_timeline_state(bucket):
    bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((set_frame, (get_current_frame(), )))
    bucket.commandQueue[__c.COMMAND_QUEUE_SETUP].append((set_frame, (bucket.settings[__c.BUCKET_SETTING_TARGET_FRAME], )))

def get_real_time(frame: float):
    return frame / float(bpy.context.scene.render.fps)