# coding=utf-8
from .basic import MachineryOperationC2S


class ElectricHeaterSubmitModifiesEvent(MachineryOperationC2S):
    name = "st:EHS"
    extra_attrs = ("power", "kelvin_limit")

    def __init__(self, x, y, z, power, kelvin_limit, player_id=""):
        # type: (int, int, int, int, int, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.power = power
        self.kelvin_limit = kelvin_limit
        self.player_id = player_id
