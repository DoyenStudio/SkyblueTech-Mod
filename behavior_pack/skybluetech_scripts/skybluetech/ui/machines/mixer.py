# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from ...ui_sync.machines.mixer import MixerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, InitFluidDisplay, UpdateFluidDisplay

from ..recipe_checker import AsRecipeCheckerBtn
from ...define.machine_config.mixer import recipes

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"
FLUID_NODE = MAIN_PATH / "fluid_display"


@RegistProxyScreen("MixerUI.main")
class MixerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = MixerUISync.NewClient(dim, x, y, z) # type: MixerUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.update_cb = InitFluidDisplay(
            self.fluid_display, 
            lambda: (
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            )
        )
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            "skybluetech:mixer",
            recipes,
        )
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        self.update_cb()
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
        UpdateFluidDisplay(
            self.fluid_display,
            self.sync.fluid_id,
            self.sync.fluid_volume,
            self.sync.max_volume,
        )

