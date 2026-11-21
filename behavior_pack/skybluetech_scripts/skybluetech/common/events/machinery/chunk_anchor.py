# coding=utf-8
from .basic import MachineryOperationC2S


class ChunkAnchorRadiusRequest(MachineryOperationC2S):
    name = "st:ChunkAnchorRadius"
    extra_attrs = ("step",)

    def __init__(self, x, y, z, step, player_id=""):
        MachineryOperationC2S.__init__(self, x, y, z, player_id)
        self.step = step
