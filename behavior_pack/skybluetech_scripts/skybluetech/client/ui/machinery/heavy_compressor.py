# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.heavy_compressor import HeavyCompressorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"


@RegistToolDeltaScreen("HeavyCompressorUI.main", is_proxy=True)
class HeavyCompressorUI(MachinePanelUIProxy):
    def __init__(self, screenName, screenNode):
        MachinePanelUIProxy.__init__(self, screenName, screenNode)

    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = HeavyCompressorUISync.NewClient(dim, x, y, z)  # type: HeavyCompressorUISync
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
