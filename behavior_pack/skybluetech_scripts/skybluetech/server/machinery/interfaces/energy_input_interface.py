# coding=utf-8
from ..core import RegisterMachine
from .base_interface import BaseInterface


@RegisterMachine
class EnergyInputInterface(BaseInterface):
    store_rf_max = 1

    def GetEnergyTransferLimits(self, period_ticks):
        machine = self.getMachineRef()
        return machine.GetEnergyTransferLimits(period_ticks) if machine is not None else (0, 0)

    def AddPower(self, rf):
        # type: (int) -> tuple[bool, int]
        m = self.getMachineRef()
        if m is None:
            return False, rf
        else:
            return m.AddPower(rf)
