# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.battery_cube import BatteryCubeUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"


@RegistToolDeltaScreen("BatteryCubeUI.main", is_proxy=True)
class BatteryCubeUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = BatteryCubeUISync.NewClient(dim, x, y, z)  # type: BatteryCubeUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power = self.GetElement(POWER_NODE)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power, self.sync.storage_rf, self.sync.rf_max)
