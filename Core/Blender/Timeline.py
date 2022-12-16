import bpy
from io_ggltf import Constants as __c
from io_ggltf.Core.Exceptions import AnimationExceptions

def set_frame(frame: float):
    bpy.context.scene.frame_float = frame

def get_current_frame():
    return bpy.context.scene.frame_float

def is_frame_step_valid(frameStart: float, frameEnd: float, frameStep: float):
    if frameStep <= 0.0:
        raise AnimationExceptions.InvalidFrameStepException(frameStart, frameEnd, frameStep)
    if (frameEnd - frameStart) % frameStep == 0.0:
        return True
    raise AnimationExceptions.InvalidFrameStepException(frameStart, frameEnd, frameStep)

def snapshot_timeline_state(bucket):
    targetFrame = bucket.settings[__c.BUCKET_SETTING_TARGET_FRAME]
    if type(targetFrame) == str:
        targetFrame = get_marker_frame(targetFrame)

    bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((set_frame, (get_current_frame(), )))
    bucket.commandQueue[__c.COMMAND_QUEUE_SETUP].append((set_frame, (targetFrame, )))

def get_real_time(frame: float):
    return frame / float(bpy.context.scene.render.fps)

def get_marker_frame(markerName: str):
    marker = bpy.context.scene.timeline_markers.get(markerName)

    if marker != None:
        return marker.frame
    raise AnimationExceptions.TimelineMarkerException(markerName)
