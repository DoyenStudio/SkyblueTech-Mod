# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.thermal_generator import ThermalGeneratorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateFlame

POWER_NODE = MAIN_PATH / "power_bar"
FLAME_NODE = MAIN_PATH / "flame"


@RegistToolDeltaScreen("ThermalGeneratorUI.main", is_proxy=True)
class ThermalGeneratorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = ThermalGeneratorUISync.NewClient(dim, x, y, z)  # type: ThermalGeneratorUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.flame = self.GetElement(FLAME_NODE)
        self.sync.SetUpdateCallback(self.WhenUpdated)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateFlame(self.flame, self.sync.rest_burn_relative)
