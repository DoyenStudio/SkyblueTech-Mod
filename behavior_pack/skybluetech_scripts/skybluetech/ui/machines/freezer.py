# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from skybluetech_scripts.tooldelta.define import Item
from ...define.events.freezer import FreezerModeChangedEvent
from ...define.machine_config.freezer import recipes
from ...ui_sync.machines.freezer import FreezerUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, InitFluidDisplay

POWER_NODE = MAIN_PATH / "power_bar"
PRGS_NODE = MAIN_PATH / "progress"
FLUID_NODE = MAIN_PATH / "fluid_disp"
MODE_CHANGE_BTN_NODE = MAIN_PATH / "mode_change"


@RegistProxyScreen("FreezerUI.main")
class FreezerUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = FreezerUISync.NewClient(dim, x, y, z) # type: FreezerUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.progress = self.GetElement(PRGS_NODE)
        self.fluid_display = self.GetElement(FLUID_NODE)
        self.mode_change_btn = self.GetElement(MODE_CHANGE_BTN_NODE).asButton()
        self.mode_change_btn.SetCallback(self.changeMode)
        self.mode_change_btn_img = self.mode_change_btn["item"].asItemRenderer()
        self.fluid_updater = InitFluidDisplay(
            self.fluid_display,
            lambda: (
                self.sync.fluid_id,
                self.sync.fluid_volume,
                self.sync.max_volume,
            )
        )
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        self.fluid_updater()
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressL2R(self.progress, self.sync.progress_relative)
        output_item = recipes[self.sync.freezer_mode].outputs["item"][0].id
        self.mode_change_btn_img.SetUiItem(Item(output_item))

    def changeMode(self, params):
        dim, x, y, z = self.pos
        next_mode = (self.sync.freezer_mode + 1) % len(recipes)
        FreezerModeChangedEvent(dim, x, y, z, next_mode).send()
