# coding=utf-8
#
from ...define.flags import DEACTIVE_FLAG_POWER_LACK
from .base_machine import BaseMachine

K_TICKS_LEFT = "ticks_left"


class BaseSpeedControl(BaseMachine):
    """
    基本的速度控制机器基类。
    
    覆写: `OnLoad`[基调用], `Dump`[基调用], `SetDeactiveFlag`[基调用]
    """
    origin_process_ticks = 20

    def OnLoad(self):
        BaseMachine.OnLoad(self)
        self.ticks_left = self.bdata[K_TICKS_LEFT] or 0.0
        self.reduce_ticks = 1

    def SetSpeedRelative(self, speed):
        # type: (float) -> None
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

    def Dump(self):
        self.bdata[K_TICKS_LEFT] = self.ticks_left
            
    def SetProcessTicks(self, ticks):
        # type: (int) -> None
        self.origin_process_ticks = ticks

    def GetProcessProgress(self):
        return 1 - float(self.ticks_left) / self.origin_process_ticks

    def ResetProgress(self):
        self.ticks_left = self.origin_process_ticks

    def SetDeactiveFlag(self, flag):
        # type: (int) -> None
        BaseMachine.SetDeactiveFlag(self, flag)
        if flag != DEACTIVE_FLAG_POWER_LACK:
            self.ResetProgress()
