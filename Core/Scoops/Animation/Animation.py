from io_ggltf.Core.AnimationDescriber import AnimationDescriber
from io_ggltf.Core.Scoops.Animation.BakedAnimation import BakedAnimation
from io_ggltf.Core.Scoops.Animation import Properties
from io_ggltf.Core.Managers import AccessorManager
from io_ggltf import Constants as __c

def scoop(bucket, describer: AnimationDescriber):
    bake = BakedAnimation(bucket, describer)
    anim = bake.get_animation()
    
    channels = []
    samplers = []

    animDict = {
        __c.ANIMATION_NAME: describer._get_name(),
        __c.ANIMATION_CHANNELS: channels,
        __c.ANIMATION_SAMPLERS: samplers
        }

    # samplers contain:
    # __c.ANIMATION_SAMPLER_INPUT: ID of accessor with keyframe times
    # __c.ANIMATION_SAMPLER_OUTPUT: ID of accessor with keyframe values
    # __c.ANIMATION_SAMPLER_INTERPOLATION: interpolation type

    # channels contain:
    # __c.ANIMATION_CHANNEL_SAMPLER: ID of the sampler
    # __c.ANIMATION_CHANNEL_TARGET: description of what this channel targets:
    #           __c.ANIMATION_CHANNEL_TARGET_NODE: ID of node to apply this channel to
    #           __c.ANIMATION_CHANNEL_TARGET_PATH: path of the property to apply this channel to
    
    for nodeID, properties in anim.items():
        for property, keys in properties.items():
            samplerID = len(samplers)
            minTime = min(keys[0])
            maxTime = max(keys[0])
            inputID = AccessorManager.add_accessor(bucket, componentType=None, type=None, packingFormat=None, data=keys[0], min=minTime, max=maxTime, minMaxAsArray=True)
            outputID = AccessorManager.add_accessor(bucket, componentType=None, type=None, packingFormat=None, data=keys[1])

            sampler = {
                __c.ANIMATION_SAMPLER_INPUT: inputID,
                __c.ANIMATION_SAMPLER_OUTPUT: outputID,
                __c.ANIMATION_SAMPLER_INTERPOLATION: 
                    __c.ANIMATION_SAMPLER_INTERPOLATION_TYPE_STEP if describer._use_step_interpolation() else __c.ANIMATION_SAMPLER_INTERPOLATION_TYPE_LINEAR
            }
            samplers.append(sampler)

            channel = {
                __c.ANIMATION_CHANNEL_SAMPLER: samplerID,
                __c.ANIMATION_CHANNEL_TARGET:{
                    __c.ANIMATION_CHANNEL_TARGET_NODE: nodeID,
                    __c.ANIMATION_CHANNEL_TARGET_PATH: property
                }
            }

            channels.append(channel)

    bucket.data[__c.BUCKET_DATA_ANIMATIONS].append(animDict)