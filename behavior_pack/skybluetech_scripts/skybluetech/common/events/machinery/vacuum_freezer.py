# coding=utf-8
from .basic import MachineryOperationC2S


class VacuumFreezerSubmitModifiesEvent(MachineryOperationC2S):
    name = "st:VFS"
    extra_attrs = ("power", "kelvin")

    def __init__(self, x, y, z, power, kelvin, player_id=""):
        # type: (int, int, int, int, float, str) -> None
        self.x = x
        self.y = y
        self.z = z
        self.power = power
        self.kelvin = kelvin
        self.player_id = player_id
