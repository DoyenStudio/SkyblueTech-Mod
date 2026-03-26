# coding=utf-8
#
from ....common.define import flags as rf_flags
from .base_machine import BaseMachine


class PowerControl(BaseMachine):
    """
    机器的额定功率控制器。
    自动控制机器的 active 状态。

    派生自: `BaseMachine`

    覆写: `AddPower (super)`
    """

    running_power = 1000
    power_pos_rate = 1.0
    power_neg_rate = 1.0

    def AddPower(self, rf):
        # type: (int) -> tuple[bool, int]
        res = BaseMachine.AddPower(self, rf)
        if self.store_rf < self.running_power:
            self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        else:
            self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        return res

    def SetPower(self, power):
        # type: (int) -> None
        self.running_power = power

    def SetPowerPositiveRate(self, rate):
        # type: (float) -> None
        "设置耗能正倍率; 仅提供给升级类用"
        self.power_rate = rate

    def SetPowerNegativeRate(self, rate):
        # type: (float) -> None
        "设置耗能负倍率; 仅提供给升级类用"
        self.power_rate = rate

    def ReducePower(self, rf=None):
        # type: (int | None) -> None
        if rf is None:
            rf = self.running_power
        BaseMachine.ReducePower(self, rf)

    def PowerEnough(self):
        "如果能量不足时先尝试向电网索取能源, 后自动将 flag 设置为缺少能源"
        # type: () -> bool
        res = self.store_rf >= self.running_power
        if res:
            self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        else:
            self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        return res
