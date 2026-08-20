# coding=utf-8
from skybluetech_scripts.skybluetech.common.events.machinery.freezer import (
    FreezerModeChangedEvent,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.freezer import (
    K_MODE,
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdateGenericProgressL2R, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
FLUID_PATH = MAIN_PATH / "fluid_disp"
MODE_CHANGE_BTN_PATH = MAIN_PATH / "mode_change"


@RegistToolDeltaScreen("FreezerUI.main", is_proxy=True)
class FreezerUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.fluid_display = self.GetElement(FLUID_PATH)
        self.mode_change_btn = self.GetElement(MODE_CHANGE_BTN_PATH).asButton()
        self.mode_change_btn.SetCallback(self.changeMode)
        self.mode_change_btn_img = self.mode_change_btn["item"].asItemRenderer()
        self.fluid_displayer = FluidDisplayer(self.fluid_display)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )
        self.freezer_mode = None

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0.0)
        self.freezer_mode = GetValue(data, K_MODE, 0)
        fluid = FluidSlotClient(data)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        output_item = recipes.recipes_mapping[self.freezer_mode].outputs["item"][0].id
        self.mode_change_btn_img.SetUiItem(Item(output_item))

    def changeMode(self, params):
        if self.freezer_mode is None:
            return
        _, x, y, z = self.pos
        next_mode = (self.freezer_mode + 1) % len(recipes)
        FreezerModeChangedEvent(x, y, z, next_mode).send()
