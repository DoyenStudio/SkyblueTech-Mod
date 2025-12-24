# coding=utf-8
#
from .base_speed_control import BaseSpeedControl
from .power_control import PowerControl


class SPControl(BaseSpeedControl, PowerControl):
    """
    速度和能量控制基类合并, 并覆写一个更方便合理的 `ProcessOne()` 方法。
    
    派生自 `BaseSpeedControl`, `PowerControl`

    覆写: `OnLoad`[基调用], `Dump`[基调用], `AddPower`[基调用], `SetDeactiveFlag`[基调用]
    """
    def ProcessOnce(self):
        """
        尝试处理一次配方, 会消耗能量, 如可处理返回 True, 制作中或能量不足返回 False
        
        值得注意的是, 我们可能要在 1tick 之内进行多次配方产出
        """
        if not self.PowerEnough():
            return False
        self.ReducePower()
        return BaseSpeedControl.ProcessOnce(self)
