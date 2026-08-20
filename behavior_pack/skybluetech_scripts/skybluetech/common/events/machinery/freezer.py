# coding=utf-8
from .basic import MachineryOperationC2S


class FreezerModeChangedEvent(MachineryOperationC2S):
    name = "st:FreezerModeChanged"
    extra_attrs = ("new_mode",)

    def __init__(self, x, y, z, new_mode, player_id=""):
        # type: (int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.new_mode = new_mode
        self.player_id = player_id
