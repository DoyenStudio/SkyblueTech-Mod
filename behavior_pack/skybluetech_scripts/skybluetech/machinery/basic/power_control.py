# coding=utf-8
#
from ...define import flags as rf_flags
from ...transmitters.wire.logic import RequireEnergyFromNetwork
from .base_machine import BaseMachine


class PowerControl(BaseMachine):
    """
    机器的额定功率控制器。
    自动控制机器的 active 状态。
    
    覆写和调用父类: `AddPower`[基调用]
    """
    running_power = 1000
    power_pos_rate = 1.0
    power_neg_rate = 1.0

    def AddPower(self, rf, is_generator=False, max_limit=None, depth=0):
        # type: (int, bool, int | None, int) -> tuple[bool, int]
        res = BaseMachine.AddPower(self, rf, is_generator, max_limit, depth)
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
        "如果能量不足时自动将 flag 设置为缺少能源"
        # type: (bool) -> bool
        res = self.store_rf >= self.running_power
        if res:
            self.UnsetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
        elif auto_require:
            self.SetDeactiveFlag(rf_flags.DEACTIVE_FLAG_POWER_LACK)
            RequireEnergyFromNetwork(self)
            return self.PowerEnough(auto_require=False)
        return res

