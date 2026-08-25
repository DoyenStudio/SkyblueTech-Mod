# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.facing import OPPOSITE_FACING
from .base_machine import BaseMachine


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
        self._output_neighbors_cache = None

    def PowerFull(self):
        "能量是否已满。"
        return self.store_rf >= self.store_rf_max

    def OnInvalidateCaches(self):
        "邻居机缓存失效: 邻居方块放置/移除/变化后调用, 下一个 tick 惰性重建。"
        self._output_neighbors_cache = None

    def _get_output_neighbors(self):
        "输出方向的邻居机列表(含朝向), 结构固定时缓存, 仅邻居变化时重建。"
        cache = self._output_neighbors_cache
        if cache is None:
            from .. import pool

            cache = self._output_neighbors_cache = list(
                pool.GetNearbyMachines(
                    self.dim, self.x, self.y, self.z, self._power_output_faces
                )
            )
        return cache

    def GeneratePower(self, rf):
        # type: (int) -> tuple[bool, int]
        """
        产出能量, 返回是否供能和能量溢出值。

        Args:
            rf (int): 能量

        Returns:
            tuple[bool, int]: 是否进行了供能, 能量溢出值
        """
        ok, rf = self._output_nearby(rf)
        _ok, rf = self._generate_power(rf)
        return ok or _ok, rf

    def _output_nearby(self, output_rf):
        # type: (int) -> tuple[bool, int]
        ok = False
        for machine, facing in self._get_output_neighbors():
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
