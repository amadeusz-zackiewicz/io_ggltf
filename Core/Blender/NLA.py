import bpy
from io_ggltf.Core import Util, BlenderUtil
from io_ggltf import Constants as __c

def set_track_mute(objAccessor, nlaTrack: str, mute: bool):
    """
    Set the mute on the specified track. Blender UI works on opposite basis,
    which means that the mute bool is flipped in the UI.
    """
    obj = Util.try_get_object(objAccessor)
    obj.animation_data.nla_tracks[nlaTrack].mute = mute


def set_track_solo(objAccessor, nlaTrack: str, solo: bool):
    """
    Set the solo on the specified track.
    """
    obj = Util.try_get_object(objAccessor)
    obj.animation_data.nla_tracks[nlaTrack].is_solo = solo

def get_track_framerange(obj, nlaTrack: str):
    """
    Get the range of frames of all strips combined.

    Args:
        obj (Blender.Object or tuple): Which object to get the track data from. Accepts accessors.
        nlaTrack (str): Name of the track

    Returns: (tuple[int, int]) A range of frames required to play the animation in full.
    """
    try:
        if type(obj) == tuple:
            obj = Util.try_get_object(obj)
        strips = obj.animation_data.nla_tracks[nlaTrack].strips
        start = 999999
        end = -999999
        for strip in strips:
            start = min(start, strip.frame_start)
            end = max(end, strip.frame_end)

        return start, end
    except:
        return 0, 0

def get_framerange_for_map(animMap: dict):
    start = 999999
    end = -999999

    for objAcc, trackNames in animMap.items():
        try:
            obj = Util.try_get_object(objAcc)
            for trackName in trackNames:
                trackRange = get_track_framerange(obj, trackName)
                start = min(start, trackRange[0])
                end = max(end, trackRange[1])
        except:
            return 0, 0

    return start, end

def mute_all(*args):
    """
    Set all tracks in the blend file to mute.
    """
    objs = bpy.data.objects

    for obj in objs:
        try:
            tracks = obj.animation_data.nla_tracks
            for track in tracks:
                track.mute = True
                track.is_solo = False
        except:
            continue

def snapshot_tracks_state(bucket):
    """
    Adds mute_all command to the setup queue and then adds command that
    restore the tracks back to the state they were before being muted.
    """
    objs = bpy.data.objects

    bucket.commandQueue[__c.COMMAND_QUEUE_SETUP].append((mute_all, (None, )))

    for obj in objs:
        objAcc = BlenderUtil.get_object_accessor(obj)
        try:
            tracks = obj.animation_data.nla_tracks
            for track in tracks:
                bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((set_track_mute, (objAcc, track.name, track.mute)))
                if track.is_solo == True:
                    # disable solo and then enable it back after export
                    bucket.commandQueue[__c.COMMAND_QUEUE_SETUP].append((set_track_solo, (objAcc, track.name, False)))
                    bucket.commandQueue[__c.COMMAND_QUEUE_CLEAN_UP].append((set_track_solo, (objAcc, track.name, True)))

        except:
            continue

def prep_tracks_for_animation(animMap: dict):
    """
    Mute all tracks except the ones required for the animation.

    Args:
        animMap (dict[tuple:list[str]]): A map describing which NLA tracks to activate for the animation
    """
    mute_all()

    for objAcc, trackName in animMap.items():
        set_track_mute(objAcc, trackName, False)

def produce_tracks_anim_map() -> dict:
    """
    Create a dictionary based on the currently unmuted tracks in the editor.
    This should be called by an operator via UI button.
    """
    d = {}

    objs = bpy.data.objects

    for obj in objs:
        unmuted = []
        try:
            tracks = obj.animation_data.nla_tracks
            for track in tracks:
                if track.mute == False:
                    unmuted.append(track.name)
        except:
            continue
        
        if len(unmuted) > 0:
            d[BlenderUtil.get_object_accessor(obj)] = unmuted

    return d