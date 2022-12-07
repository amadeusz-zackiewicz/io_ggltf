from io_ggltf import Constants as __c
from io_ggltf.Core.Decorators import ShowInUI as __ShowInUI
from io_ggltf.Core.AnimationDescriber import AnimationDescriber

@__ShowInUI()
def create_describer(name: str, frameStart=None, frameEnd=None):
    return AnimationDescriber(name=name, frameStart=frameStart, frameEnd=frameEnd)

@__ShowInUI()
def add(bucket, animDescriber: AnimationDescriber):
    pass