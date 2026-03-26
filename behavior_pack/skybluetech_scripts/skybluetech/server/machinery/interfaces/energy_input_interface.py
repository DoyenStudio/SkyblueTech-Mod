# coding=utf-8
from ..basic import BaseMachine, RegisterMachine
from .base_interface import BaseInterface


@RegisterMachine
class EnergyInputInterface(BaseInterface):
    store_rf_max = 1

    def AddPower(self, rf):
        # type: (int) -> tuple[bool, int]
        print self.x, self.y, self.z, "GetPower", rf
        m = self.getMachineRef()
        if m is None:
            print "But no ref"
            return False, rf
        else:
            # import weakref

            # print("Still add", weakref.getweakrefcount(m), m.x, m.y, m.z)
            ok, res = m.AddPower(rf)
            print self.x, self.y, self.z, "And ret", res
            return ok, res
