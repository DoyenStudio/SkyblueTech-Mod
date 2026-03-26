# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define import flags
from ....common.define.facing import OPPOSITE_FACING
from .base_machine import BaseMachine


def requireWireModule():
    global GetContainerNode, pool
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import logic_module
    from .. import pool

    GetContainerNode = logic_module.GetContainerNode
    requireWireModule.has_cache = True


requireWireModule.has_cache = False


class BasePowerProvider(BaseMachine):
    """
    能量提供类机器的基类。
    提供了 GeneratePower() 方法。

    派生自: `BaseMachine`

    """

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode) if n == 1
        )

    def PowerFull(self):
        "能量是否已满。"
        return self.store_rf >= self.store_rf_max

    def GeneratePower(self, rf):
        # type: (int) -> tuple[bool, int]
        "产出能量, 返回是否供能和能量溢出值。"
        ok, rf = self._output_nearby(rf)
        _ok, rf = self._generate_power(rf)
        return ok or _ok, rf

    def _output_nearby(self, output_rf):
        # type: (int) -> tuple[bool, int]
        requireWireModule()
        ok = False
        for machine, facing in pool.GetNearbyMachines(
            self.dim, self.x, self.y, self.z, self._power_output_faces
        ):
            io_mode = machine.energy_io_mode[OPPOSITE_FACING[facing]]
            if io_mode != 0:
                continue
            _ok, output_rf = machine.AddPower(output_rf)
            ok = ok or _ok
            if output_rf <= 0:
                break
        return ok, output_rf

    def _generate_power(self, rf):
        # type: (int) -> tuple[bool, int]
        """产能, 但不向电网供能。"""
        store_rf = self.store_rf
        overflow = max(0, store_rf + rf - self.store_rf_max)
        self.store_rf = store_rf + rf - overflow
        return self.store_rf > store_rf, overflow
