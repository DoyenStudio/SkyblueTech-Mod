# coding=utf-8
from .basic import MachineryOperationC2S


class SeawaterPumpModeRequest(MachineryOperationC2S):
    name = "st:SeawaterPumpMode"
    extra_attrs = ("mode",)

    def __init__(self, x, y, z, mode, player_id=""):
        MachineryOperationC2S.__init__(self, x, y, z, player_id)
        self.mode = mode
