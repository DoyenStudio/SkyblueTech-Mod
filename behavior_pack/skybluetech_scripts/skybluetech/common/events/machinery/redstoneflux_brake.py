# coding=utf-8
from .basic import MachineryOperationC2S


class RedstoneFluxBrakeModeSwitchRequest(MachineryOperationC2S):
    name = "st:RFBMSR"
    extra_attrs = ("invert_redstone",)

    def __init__(self, x, y, z, invert_redstone, player_id=""):
        # type: (int, int, int, bool, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.invert_redstone = invert_redstone
        self.player_id = player_id
