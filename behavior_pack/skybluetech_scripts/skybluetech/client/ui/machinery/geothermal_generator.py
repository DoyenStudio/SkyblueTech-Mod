# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.geothermal_generator import GeoThermalGeneratorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateFlame, InitFluidsDisplay

POWER_NODE = MAIN_PATH / "power_bar"
FLUID_LAVA_NODE = MAIN_PATH / "lava_display"
FLUID_WATER_NODE = MAIN_PATH / "water_display"
FLAME_NODE = MAIN_PATH / "flame"


@RegistToolDeltaScreen("GeoThermalGeneratorUI.main", is_proxy=True)
class GeoThermalGeneratorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = GeoThermalGeneratorUISync.NewClient(dim, x, y, z)  # type: GeoThermalGeneratorUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.lava_display = self.GetElement(FLUID_LAVA_NODE)
        self.water_display = self.GetElement(FLUID_WATER_NODE)
        self.flame = self.GetElement(FLAME_NODE)
        self.sync.WhenUpdated = self.WhenUpdated
        self.fluid_updater1 = InitFluidsDisplay(self.lava_display, self.sync.fluids, 0)
        self.fluid_updater2 = InitFluidsDisplay(self.water_display, self.sync.fluids, 1)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateFlame(self.flame, self.sync.progress)
        self.fluid_updater1()
        self.fluid_updater2()
