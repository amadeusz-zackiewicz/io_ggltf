from io_ggltf import Constants as __c
from io_ggltf.Core import ShowFunction
from io_ggltf.Core.AnimationDescriber import AnimationDescriber
from io_ggltf.Core.Scoops.Animation import Animation
from warnings import deprecated

@deprecated("Advanced.Animation.create_describer is deprecated and might not function as intended")
def create_describer(name: str, frameStart=None, frameEnd=None, frameStep=None, useStepInterpolation=None, optimiseKeys=None):
    return AnimationDescriber(name=name, frameStart=frameStart, frameEnd=frameEnd, frameStep=frameStep, useStepInterpolation=useStepInterpolation, optimiseKeys=optimiseKeys)

@deprecated("Advanced.Animation.add is deprecated, it will be removed in future versions and might not function as intended.")
def add(bucket, animDescriber: AnimationDescriber):
    copyDescriber = animDescriber.copy()

    bucket.commandQueue[__c.COMMAND_QUEUE_ANIMATION].append((Animation.scoop, (bucket, copyDescriber)))

#ShowFunction.Register(create_describer, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Animation-Module#create_describer")
#ShowFunction.Register(add, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Animation-Module#add")