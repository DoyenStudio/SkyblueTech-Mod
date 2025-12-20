# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from ...ui_sync.machines.redstone_furnace import RedstoneFurnaceUISync
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, UpdateFlame
from .define import MachinePanelUIProxy, MAIN_PATH

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"
FLAME_NODE = MAIN_PATH / "flame"


@RegistProxyScreen("RedstoneFurnaceUI.main")
class RedstoneFurnaceUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = RedstoneFurnaceUISync.NewClient(dim, x, y, z) # type: RedstoneFurnaceUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        self.flame = self.GetElement(FLAME_NODE)
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
        UpdateFlame(self.flame, float(self.sync.storage_rf) / self.sync.rf_max)

