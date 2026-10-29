# coding=utf-8
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.core.pool import (
    GetLoadedMachine,
    GetNearbyMachines,
)
from skybluetech_scripts.skybluetech.server.machinery.interfaces.base_heat_interface import BaseHeatInterface


@RegisterMachine
class HeatOutputInterface(BaseHeatInterface):
    """每个热周期将控制器热量导向六面邻居; 拒绝外部输入。"""

    WORK_INTERVAL = 5

    def __init__(self, dim, x, y, z, block_entity_data):
        super(HeatOutputInterface, self).__init__(dim, x, y, z, block_entity_data)
        self._heat_output_ticks = 0
        self.handler.SubscribeOnTicking(self._heat_output_interface_on_ticking)

    def _heat_output_interface_on_ticking(self):
        self._heat_output_ticks += 1
        if self._heat_output_ticks < self.WORK_INTERVAL:
            return
        self._heat_output_ticks = 0
        if GetLoadedMachine(self.dim, self.x, self.y, self.z) is not self:
            return
        machine = self.getMachineRef()
        if machine is None:
            return
        for neighbor, _ in GetNearbyMachines(self.dim, self.x, self.y, self.z):
            machine.TransferHeatTo(neighbor, dt=self.WORK_INTERVAL)
