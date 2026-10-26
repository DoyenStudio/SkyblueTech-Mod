# coding=utf-8
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.skybluetech.server.machinery.interfaces.base_heat_interface import BaseHeatInterface


@RegisterMachine
class HeatInputInterface(BaseHeatInterface):
    """外部热机经此接口向控制器传热; 不主动输出。"""

    def GetHeatInputTarget(self):
        # type: () -> HeatCtrl | None
        return self.getMachineRef()
