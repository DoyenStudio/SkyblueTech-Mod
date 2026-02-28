# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.forester import ForesterUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"


@RegistToolDeltaScreen("ForesterUI.main", is_proxy=True)
class ForesterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = ForesterUISync.NewClient(dim, x, y, z)  # type: ForesterUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
