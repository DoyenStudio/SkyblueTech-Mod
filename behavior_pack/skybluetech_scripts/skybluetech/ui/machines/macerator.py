# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from ...ui_sync.machines.macerator import MaceratorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"


@RegistProxyScreen("MaceratorUI.main")
class MaceratorUI(MachinePanelUIProxy):

    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = MaceratorUISync.NewClient(dim, x, y, z) # type: MaceratorUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)

