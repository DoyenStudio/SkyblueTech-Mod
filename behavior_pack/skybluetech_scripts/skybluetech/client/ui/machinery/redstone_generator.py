# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.redstone_generator import RedstoneGeneratorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateFlame, UpdateGenericProgressL2R

POWER_NODE = MAIN_PATH / "power_bar"
FLAME_NODE = MAIN_PATH / "flame"
PROGRESS_NODE = MAIN_PATH / "progress"


@RegistToolDeltaScreen("RedstoneGeneratorUI.main", is_proxy=True)
class RedstoneGeneratorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = RedstoneGeneratorUISync.NewClient(dim, x, y, z)  # type: RedstoneGeneratorUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.flame = self.GetElement(FLAME_NODE)
        self.progress = self.GetElement(PROGRESS_NODE)
        self.sync.SetUpdateCallback(self.WhenUpdated)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateFlame(self.flame, self.sync.rest_burn_relative)
        UpdateGenericProgressL2R(self.progress, 1 - self.sync.rest_burn_relative)
