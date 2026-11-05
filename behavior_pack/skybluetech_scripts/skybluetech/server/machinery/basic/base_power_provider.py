# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.facing import FACING_DXYZ, OPPOSITE_FACING
from .base_machine import BaseMachine


class BasePowerProvider(BaseMachine):
    """
    能量提供类机器的基类。
    提供了 GeneratePower() 方法。

    派生自: `BaseMachine`

    """

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BasePowerProvider, self).__init__(dim, x, y, z, block_entity_data)
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode) if n == 1
        )
        self._output_neighbors_cache = None
        self.handler.SubscribeOnInvalidateCaches(self._base_power_provider_on_invalidate_caches)

    def PowerFull(self):
        "能量是否已满。"
        return self.store_rf >= self.store_rf_max

    def _base_power_provider_on_invalidate_caches(self):
        "邻居机缓存失效: 邻居方块放置/移除/变化后调用, 下一个 tick 惰性重建。"
        self._output_neighbors_cache = None

    def _resolve_output_face(self, facing):
        from ...export.energy import GetEnergyHandler

        dx, dy, dz = FACING_DXYZ[facing]
        pos = (self.x + dx, self.y + dy, self.z + dz)
        face = OPPOSITE_FACING[facing]
        target = GetEnergyHandler(pos, self.dim, face, native_only=True)
        entry = (pos, face, target)
        self._output_neighbors_cache[facing] = entry
        return entry

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
        from ...export.energy import _get_external_energy_handler

        ok = False
        for facing in self._power_output_faces:
            if self._output_neighbors_cache is None:
                self._output_neighbors_cache = {}
            entry = self._output_neighbors_cache.get(facing)
            if entry is None or (entry[2] is not None and not entry[2].valid()):
                entry = self._resolve_output_face(facing)
            pos, face, target = entry
            if target is None:
                # 外部 resolver 可随时改变端点；只缓存本包机器或其缺席。
                target = _get_external_energy_handler(pos, self.dim, face)
            if target is None or not target.canReceive() or not target.acceptsActivePush():
                continue
            try:
                accepted = target.insert(int(output_rf))
            except Exception as error:
                # 接收方可能已经入账，不能把结果不明的电量再次放回发电机。
                print("[skybluetech] uncertain adjacent energy transfer: %s" % error)
                return True, 0
            output_rf -= accepted
            ok = ok or accepted > 0
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
