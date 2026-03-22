# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define import flags
from ....common.define.facing import OPPOSITE_FACING
from .base_machine import BaseMachine


def requireWireModule():
    global GetContainerNode, pool, PushEnergyIntoNetwork
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import logic_module, PushEnergyIntoNetwork
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
        self._reset_send_energy_retries()

    def OnTryActivate(self):
        self._reset_send_energy_retries()

    def OnTicking(self):
        if self.store_rf_max > self.store_rf:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
        if self._can_output_energy():
            ok, self.store_rf = self._output(self.store_rf)
            if not ok:
                self._add_send_energy_retries()
            else:
                self._reset_send_energy_retries()

    def PowerFull(self):
        "能量是否已满。"
        return self.store_rf >= self.store_rf_max

    def GeneratePower(self, rf):
        # type: (int) -> tuple[bool, int]
        "产出能量, 返回是否供能和能量溢出值。"
        ok = False
        if self._can_output_energy():
            _ok, rf = self._output(rf)
            ok = ok or _ok
        _ok, overflow = self._generate_power(rf)
        return ok or _ok, overflow

    def _generate_power(self, rf):
        # type: (int) -> tuple[bool, int]
        """产能, 但不向电网供能。"""
        store_rf = self.store_rf
        overflow = max(0, store_rf + rf - self.store_rf_max)
        self.store_rf = store_rf + rf - overflow
        return self.store_rf > store_rf, overflow

    def _output(self, rf=0, passed=None):
        # type: (int, set[BaseMachine] | None) -> tuple[bool, int]
        """向电网供能, 包括周围的机器。"""
        if passed is None:
            passed = set()
        output_rf = self.store_rf + rf
        store_rf_max = self.store_rf_max
        requireWireModule()
        output_networks = set(
            GetContainerNode(
                self.dim, self.x, self.y, self.z, enable_cache=True
            ).outputs.values()
        )
        ok = False
        for network in output_networks:
            if network is None:
                continue
            _ok, output_rf = PushEnergyIntoNetwork(network, output_rf, passed)
            ok = ok or _ok
            if output_rf <= 0:
                break
        if output_rf > 0:
            for machine, facing in pool.GetNearbyMachines(
                self.dim, self.x, self.y, self.z, self._power_output_faces
            ):
                io_mode = machine.energy_io_mode[OPPOSITE_FACING[facing]]
                if io_mode != 0:
                    continue
                _ok, output_rf = machine.AddPower(output_rf, None, passed)
                ok = ok or _ok
                if output_rf <= 0:
                    break
        self.store_rf = min(store_rf_max, output_rf)
        overflow = max(0, output_rf - self.store_rf_max)
        return ok, overflow

    def _can_output_energy(self):
        # type: () -> bool
        return self._sending_energy_retries < 20

    def _add_send_energy_retries(self):
        # type: () -> None
        self._sending_energy_retries += 1

    def _reset_send_energy_retries(self):
        # type: () -> None
        self._sending_energy_retries = 0
