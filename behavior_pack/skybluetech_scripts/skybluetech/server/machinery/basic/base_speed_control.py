# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ....common.define.flags import DEACTIVE_FLAG_POWER_LACK
from .base_machine import BaseMachine

K_TICKS_LEFT = "ticks_left"


class BaseSpeedControl(BaseMachine):
    """
    基本的速度控制机器基类。

    覆写:
        `OnLoad (super)`
        `Dump (super)`
        `SetDeactiveFlag (super)`
    """

    origin_process_ticks = 20

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.reduce_ticks = 1
        self._cached_ticks_left = self.bdata[K_TICKS_LEFT] or self.origin_process_ticks

    def SetSpeedRelative(self, speed):
        # type: (float) -> None
        """
        设置相对速度。默认为 1

        Args:
            speed (float): 相对速度
        """
        self.reduce_ticks = speed

    def ProcessOnce(self):
        """
        尝试处理一次配方, 如可处理返回 True, 制作中返回 False

        值得注意的是, 我们可能要在 1tick 之内进行多次配方产出
        """
        if self.ticks_left <= 0:
            self.ticks_left += self.origin_process_ticks
            return True
        else:
            self.ticks_left -= self.reduce_ticks
            return False

    def SetProcessTicks(self, ticks):
        # type: (int) -> None
        """
        设置工作一次所需 ticks。

        Args:
            ticks (int): mc game ticks
        """
        self.origin_process_ticks = ticks

    def GetProcessProgress(self):
        """
        获取工作进度 (最多为 1)。

        Returns:
            float: 工作进度, 0~1
        """
        return 1 - float(self.ticks_left) / self.origin_process_ticks

    def ResetProgress(self):
        """
        重置工作进度。
        """
        self.ticks_left = self.origin_process_ticks

    @SuperExecutorMeta.execute_super
    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        if flag != DEACTIVE_FLAG_POWER_LACK:
            self.ResetProgress()

    @property
    def ticks_left(self):
        return self._cached_ticks_left

    @ticks_left.setter
    def ticks_left(self, value):
        # type: (float) -> None
        self._cached_ticks_left = self.bdata[K_TICKS_LEFT] = value
