# coding=utf-8
from mod.server.blockEntityData import BlockEntityData  # noqa: F401
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define.facing import OPPOSITE_FACING
from .base_machine import BaseMachine
from .gui_ctrl import GUIControl


def requireWireModule():
    global GetContainerNode, pool, PushEnergyIntoNetwork
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import logic_module, PushEnergyIntoNetwork
    from .. import pool

    GetContainerNode = logic_module.GetContainerNode
    requireWireModule.has_cache = True


requireWireModule.has_cache = False


class BaseGenerator(BaseMachine):
    """
    发电机基类。
    提供了 GeneratePower() 方法。

    派生自: `BaseMachine`

    """

    __metaclass__ = SuperExecutorMeta

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode) if n == 1
        )

    def GeneratePower(self, rf):
        # type: (int) -> bool
        "产出能量。"
        srf = self.store_rf = min(
            self.store_rf_max, self.add_power_into_wire_network(self.store_rf + rf)
        )
        if isinstance(self, GUIControl):
            self.OnSync()
        return srf != rf

    def GeneratePowerWithOverflow(self, rf):
        # type: (int) -> tuple[bool, int]
        "仅产出能量并直接添加到电网。"
        overflow = self.add_power_into_wire_network(rf)
        if isinstance(self, GUIControl):
            self.OnSync()
        return rf != overflow, overflow

    def add_power_into_wire_network(self, rf, passed=None):
        # type: (int, set[BaseMachine] | None) -> int
        """在已连接的电缆网络中为机器添加能量, 包括周围的机器。 返回溢出的能量"""
        if passed is None:
            passed = set()
        requireWireModule()
        output_networks = set(
            GetContainerNode(
                self.dim, self.x, self.y, self.z, enable_cache=True
            ).outputs.values()
        )
        for network in output_networks:
            if network is None:
                continue
            updated, rf = PushEnergyIntoNetwork(network, rf, passed)
            if rf <= 0:
                break
        if rf != 0:
            for machine, facing in pool.GetNearbyMachines(
                self.dim, self.x, self.y, self.z, self._power_output_faces
            ):
                io_mode = machine.energy_io_mode[OPPOSITE_FACING[facing]]
                if io_mode != 0:
                    continue
                updated, rf = machine.AddPower(rf, None, passed)
                if rf <= 0:
                    break
        return rf
