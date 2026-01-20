# coding=utf-8
#
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ...ui_sync.machinery.farming_station import FarmingStationUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"


@RegistToolDeltaScreen("FarmingStationUI.main", is_proxy=True)
class FarmingStationUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FarmingStationUISync.NewClient(dim, x, y, z) # type: FarmingStationUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
