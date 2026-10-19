# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.id_enum import Upgraders
from .base_power_provider import BasePowerProvider
from .upgrade_control import UpgradeControl


class BaseGenerator(BasePowerProvider):
    """
    发电机基类, 适合产出稳定的发电机器使用。
    提供了 SetPower() 方法。
    如果需要对溢出发电量进行管理或者控制单次的发电量, 请使用 BasePowerProvider。

    派生自: `BaseMachine`

    覆写:
        - `__init__`
        - `OnTicking`
    """

    def __init__(self, dim, x, y, z, block_entity_data):
        super(BaseGenerator, self).__init__(dim, x, y, z, block_entity_data)
        self._power_output_faces = tuple(
            i for i, n in enumerate(self.energy_io_mode) if n == 1
        )
        self.output_power = 0
        self.handler.SubscribeOnTicking(self._base_generator_on_ticking)

    def _base_generator_on_ticking(self):
        if self.IsActive():
            self.GeneratePower(self.output_power)
            if self.PowerFull():
                if isinstance(self, UpgradeControl) and self.HasUpgrader(
                    Upgraders.GENERIC_AUTOSTOP
                ):
                    self.SetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_FULL)
        elif self.store_rf > 0:
            _, self.store_rf = self._output_nearby(self.store_rf)

    def SetOutputPower(self, power):
        # type: (int) -> None
        """
        设置发电机输出功率。

        Args:
            power (int): 新的输出功率值
        """
        self.output_power = power
