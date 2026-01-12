# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ...ui_sync.machines.charger import ChargerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"


@RegistToolDeltaScreen("ChargerUI.main", is_proxy=True)
class ChargerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = ChargerUISync.NewClient(dim, x, y, z) # type: ChargerUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power = self.GetElement(POWER_NODE)
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power, self.sync.storage_rf, self.sync.rf_max)

