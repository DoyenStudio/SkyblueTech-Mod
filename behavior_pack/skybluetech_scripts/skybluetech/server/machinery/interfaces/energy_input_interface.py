# coding=utf-8
from ..basic import BaseMachine, RegisterMachine
from .base_interface import BaseInterface


@RegisterMachine
class EnergyInputInterface(BaseInterface):
    store_rf_max = 1

    def AddPower(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        m = self.getMachineRef()
        if m is None:
            # print("REF is None")
            return False, rf
        else:
            # import weakref

            # print("Still add", weakref.getweakrefcount(m), m.x, m.y, m.z)
            return m.AddPower(rf, max_limit, passed)
