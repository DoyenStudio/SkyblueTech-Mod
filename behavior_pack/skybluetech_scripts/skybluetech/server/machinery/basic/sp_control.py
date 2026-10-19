# coding=utf-8
#
from .base_speed_control import BaseSpeedControl
from .power_control import PowerControl


class SPControl(PowerControl, BaseSpeedControl):
    """
    速度和能量控制基类合并, 并覆写一个更方便合理的 `ProcessOnce()` 方法。

    派生自:
        `BaseMachine`
        `BaseSpeedControl`
        `PowerControl`
    """

    def ProcessOnce(self):
        """
        尝试处理一次配方, 会消耗能量, 如可处理返回 True, 制作中或能量不足返回 False

        值得注意的是, 我们可能要在 1tick 之内进行多次配方产出

        Returns:
            bool: 是否已处理完一次配方, 可以结束配方运行
        """
        if not self.PowerEnough():
            return False
        self.ReducePower()
        return BaseSpeedControl.ProcessOnce(self)
