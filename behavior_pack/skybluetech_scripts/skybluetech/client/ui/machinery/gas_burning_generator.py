# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ....common.ui_sync.machinery.gas_burning_generator import GasBurningGeneratorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateFlame, InitFluidsDisplay

POWER_NODE = MAIN_PATH / "power_bar"
GAS_INPUT_NODE = MAIN_PATH / "gas_input"
GAS_OUTPUT_NODE = MAIN_PATH / "gas_output"
FLAME_NODE = MAIN_PATH / "flame"


@RegistToolDeltaScreen("GasBurningGeneratorUI.main", is_proxy=True)
class GasBurningGeneratorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = GasBurningGeneratorUISync.NewClient(dim, x, y, z)  # type: GasBurningGeneratorUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.gas_input = self.GetElement(GAS_INPUT_NODE)
        self.gas_output = self.GetElement(GAS_OUTPUT_NODE)
        self.flame = self.GetElement(FLAME_NODE)
        self.sync.SetUpdateCallback(self.WhenUpdated)
        self.fluid_updater1 = InitFluidsDisplay(self.gas_input, self.sync.fluids, 0)
        self.fluid_updater2 = InitFluidsDisplay(self.gas_output, self.sync.fluids, 1)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateFlame(self.flame, self.sync.progress)
        self.fluid_updater1()
        self.fluid_updater2()
