# coding=utf-8


class BasicFluidTexture(object):
    def __init__(self, texture_path, flipbook_frames, ticks_per_frame=1):
        # type: (str, int, int) -> None
        self.texture_path = texture_path
        self.flipbook_frames = flipbook_frames
        self.ticks_per_frame = ticks_per_frame


class FluidTexture(object):
    def __init__(self, rgb, alpha, basic_texture):
        # type: (tuple[int, int, int], int, BasicFluidTexture) -> None
        self.rgb = rgb
        self.alpha = alpha
        self.basic_texture = basic_texture
