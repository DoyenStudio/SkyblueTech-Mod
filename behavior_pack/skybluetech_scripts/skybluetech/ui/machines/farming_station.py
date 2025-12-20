# coding=utf-8
#
from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from ...ui_sync.machines.farming_station import FarmingStationUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"


@RegistProxyScreen("FarmingStationUI.main")
class FarmingStationUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FarmingStationUISync.NewClient(dim, x, y, z) # type: FarmingStationUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
