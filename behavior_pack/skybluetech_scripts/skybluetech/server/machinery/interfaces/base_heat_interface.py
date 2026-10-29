# coding=utf-8
from skybluetech_scripts.skybluetech.server.machinery.basic.heat_ctrl import HeatCtrl
from skybluetech_scripts.skybluetech.server.machinery.core.pool import GetLoadedMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces.base_interface import BaseInterface


class BaseHeatInterface(BaseInterface):
    """只代理控制器的热量, 不持有热容、热值或环境换热状态。"""

    is_non_energy_machine = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BaseHeatInterface, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnUnload(self.UnsetMachineRef)

    def SetMachineRef(self, machine):
        # type: (HeatCtrl) -> None
        if not isinstance(machine, HeatCtrl):
            raise TypeError("Heat interfaces require a HeatCtrl controller")
        super(BaseHeatInterface, self).SetMachineRef(machine)

    def getMachineRef(self):
        # type: () -> HeatCtrl | None
        machine = super(BaseHeatInterface, self).getMachineRef()
        if machine is None:
            return None
        if GetLoadedMachine(machine.dim, machine.x, machine.y, machine.z) is not machine:
            return None
        return machine

    def GetHeatInputTarget(self):
        # type: () -> HeatCtrl | None
        "默认拒绝输入; 只有受热口覆写为控制器。"
        return None
