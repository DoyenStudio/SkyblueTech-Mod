# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define import flags
from ....common.define.facing import OPPOSITE_FACING
from ....common.define.id_enum import Upgraders
from .base_machine import BaseMachine
from .base_power_provider import BasePowerProvider
from .upgrade_control import UpgradeControl


def requireWireModule():
    global GetContainerNode, pool, PushEnergyIntoNetwork
    if requireWireModule.has_cache:
        return
    from ...transmitters.wire.logic import logic_module, PushEnergyIntoNetwork
    from .. import pool

    GetContainerNode = logic_module.GetContainerNode
    requireWireModule.has_cache = True


requireWireModule.has_cache = False


class BaseGenerator(BasePowerProvider):
    """
    发电机基类。
    提供了 SetPower() 方法。
    如果需要对溢出发电量进行管理或者控制单次的发电量, 请使用 BasePowerProvider。

    派生自: `BaseMachine`

    """

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode) if n == 1
        )
        self._reset_send_energy_retries()
        self.output_power = 0

    def OnTicking(self):
        if self.IsActive():
            if self._can_output_energy():
                ok, overflow = self._output(self.output_power)
                if not ok:
                    self._add_send_energy_retries()
                else:
                    self._reset_send_energy_retries()
                if overflow > 0:
                    self._generate_power(overflow)
                if not self.PowerFull():
                    self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            else:
                self._generate_power(self.output_power)
            if self.PowerFull():
                if isinstance(self, UpgradeControl) and self.HasUpgrader(
                    Upgraders.GENERIC_AUTOSTOP
                ):
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
        elif self._can_output_energy():
            ok, self.store_rf = self._output(self.output_power)
            if not ok:
                self._add_send_energy_retries()
            else:
                self._reset_send_energy_retries()

    @SuperExecutorMeta.execute_super
    def OnTryActivate(self):
        if self.store_rf_max > self.store_rf:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)

    def SetOutputPower(self, power):
        self.output_power = power
