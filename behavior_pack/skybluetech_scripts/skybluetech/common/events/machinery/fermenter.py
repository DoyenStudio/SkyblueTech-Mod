# coding=utf-8
from .basic import MachineryOperationC2S


class FermenterSetTemperatureEvent(MachineryOperationC2S):
    name = "st:FST"
    extra_attrs = ("temperature",)

    def __init__(self, x, y, z, temperature, player_id=""):
        # type: (int, int, int, float, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.temperature = temperature
        self.player_id = player_id


class FermenterSeMaxVolumeEvent(MachineryOperationC2S):
    name = "st:FSMV"
    extra_attrs = ("volume",)

    def __init__(self, x, y, z, volume, player_id=""):
        # type: (int, int, int, float, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.volume = volume
        self.player_id = player_id
