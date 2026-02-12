# coding=utf-8
#
from ...define import flags as rf_flags
from ...transmitters.wire.logic import RequireEnergyFromNetwork
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

    def AddPower(self, rf, max_limit=None, passed=None):
        # type: (int, int | None, set[BaseMachine] | None) -> tuple[bool, int]
        res = BaseMachine.AddPower(self, rf, max_limit, passed)
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

    def PowerEnough(self, auto_require=True):
        "如果能量不足时先尝试向电网索取能源, 后自动将 flag 设置为缺少能源"
        # type: (bool) -> bool
        res = self.store_rf >= self.running_power
        if res:
            if self.HasDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK):
                self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        elif auto_require:
            RequireEnergyFromNetwork(self)
            return self.PowerEnough(auto_require=False)
        else:
            self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        return res
