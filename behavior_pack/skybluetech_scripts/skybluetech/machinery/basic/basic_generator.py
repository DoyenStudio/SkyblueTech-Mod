# coding=utf-8
from ...define.facing import OPPOSITE_FACING
from .base_machine import BaseMachine
from .gui_ctrl import GUIControl


def requireWireModule():
    global GetNearbyWireNetworks, pool
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import (
        GetNearbyWireNetworks,
    )
    from .. import pool
    requireWireModule.has_cache = True
requireWireModule.has_cache = False


class BasicGenerator(BaseMachine):
    """
    发电机基类。
    提供了 GeneratePower() 方法。

    派生自: `BaseMachine`

    """
    def GeneratePower(self, rf):
        # type: (int) -> bool
        "产出能量。"
        self.store_rf = min(self.store_rf_max, self.addPowerIntoWireNetwork(self.store_rf + rf))
        if isinstance(self, GUIControl):
            self.OnSync()
        return self.store_rf != rf

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode)
            if n == 1
        )

    def addPowerIntoWireNetwork(self, rf, passed=None):
        # type: (int, set[BaseMachine] | None) -> int
        """ 在已连接的电缆网络中为机器添加能量, 包括周围的机器。 返回溢出的能量 """
        if passed is None:
            passed = set()
        requireWireModule()
        output_networks = GetNearbyWireNetworks(
            self.dim, self.x, self.y, self.z, enable_cache=True
        )[1]
        for network in output_networks:
            if network is None:
                continue
            for ap in network.get_input_access_points():
                machine = pool.GetMachineStrict(self.dim, *ap.target_pos)
                if machine is not None and not machine.is_non_energy_machine:
                    updated, rf = machine.AddPower(rf, network.get_power_limit(), passed)
                    if updated and isinstance(machine, GUIControl):
                        machine.OnSync()
                    if rf == 0:
                        break
        if rf != 0:
            for machine, facing in pool.GetNearbyMachines(
                self.dim, self.x, self.y, self.z, self._power_output_faces
            ):
                io_mode = machine.energy_io_mode[OPPOSITE_FACING[facing]]
                if io_mode != 0:
                    continue
                updated, rf = machine.AddPower(rf, None, passed)
                if rf == 0:
                    break
        return rf
