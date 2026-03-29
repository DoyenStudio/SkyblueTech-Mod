# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define import flags
from ....common.define.id_enum import Upgraders
from .base_power_provider import BasePowerProvider
from .upgrade_control import UpgradeControl


class BaseGenerator(BasePowerProvider):
    """
    发电机基类, 适合产出稳定的发电机器使用。
    提供了 SetPower() 方法。
    如果需要对溢出发电量进行管理或者控制单次的发电量, 请使用 BasePowerProvider。

    派生自: `BaseMachine`

    """

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode) if n == 1
        )
        self.output_power = 0

    def OnTicking(self):
        if self.IsActive():
            self.GeneratePower(self.output_power)
            if self.PowerFull():
                if isinstance(self, UpgradeControl) and self.HasUpgrader(
                    Upgraders.GENERIC_AUTOSTOP
                ):
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)

    def SetOutputPower(self, power):
        # type: (int) -> None
        self.output_power = power
