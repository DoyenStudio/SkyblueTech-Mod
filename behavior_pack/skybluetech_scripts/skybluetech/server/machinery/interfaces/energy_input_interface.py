# coding=utf-8
from ..basic import RegisterMachine
from .base_interface import BaseInterface


@RegisterMachine
class EnergyInputInterface(BaseInterface):
    store_rf_max = 1

    def AddPower(self, rf):
        # type: (int) -> tuple[bool, int]
        m = self.getMachineRef()
        if m is None:
            return False, rf
        else:
            return m.AddPower(rf)
