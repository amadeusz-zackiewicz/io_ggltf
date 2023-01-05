from io_ggltf import Constants as __c
from io_ggltf.Core import ShowFunction
from io_ggltf.Core.AnimationDescriber import AnimationDescriber
from io_ggltf.Core.Scoops.Animation import Animation

def create_describer(name: str, frameStart=None, frameEnd=None, frameStep=None, useSteppedInterpolation=None, optimiseKeys=None):
    return AnimationDescriber(name=name, frameStart=frameStart, frameEnd=frameEnd, frameStep=frameStep, useSteppedInterpolation=useSteppedInterpolation, optimiseKeys=optimiseKeys)

def add(bucket, animDescriber: AnimationDescriber):
    copyDescriber = animDescriber.copy()

    bucket.commandQueue[__c.COMMAND_QUEUE_ANIMATION].append((Animation.scoop, (bucket, copyDescriber)))

ShowFunction.Register(create_describer, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Animation-Module#create_describer")
ShowFunction.Register(add, "https://github.com/amadeusz-zackiewicz/io_ggltf/wiki/Animation-Module#add")