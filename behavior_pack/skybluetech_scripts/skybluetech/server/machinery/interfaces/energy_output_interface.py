# coding=utf-8
from ..basic import BasePowerProvider
from ..core import RegisterMachine
from .base_interface import BaseInterface


@RegisterMachine
class EnergyOutputInterface(BasePowerProvider, BaseInterface):
    store_rf_max = 160000

    def __init__(self, dim, x, y, z, block_entity_data):
        super(EnergyOutputInterface, self).__init__(dim, x, y, z, block_entity_data)

    def TakeoutPower(self, rf):
        m = self.getMachineRef()
        if m is None:
            return 0
        else:
            return m.TakeoutPower(rf)

    def GivebackPower(self, rf):
        m = self.getMachineRef()
        if m is not None:
            m.GivebackPower(rf)

    def OutputPower(self, rf):
        # type: (int) -> tuple[bool, int]
        return self.GeneratePower(rf)
