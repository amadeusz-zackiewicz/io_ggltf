from io_ggltf.Core.AnimationDescriber import AnimationDescriber
from io_ggltf.Core.Scoops.Animation.BakedAnimation import BakedAnimation

def scoop(bucket, describer: AnimationDescriber):
    anim = BakedAnimation(bucket, describer)