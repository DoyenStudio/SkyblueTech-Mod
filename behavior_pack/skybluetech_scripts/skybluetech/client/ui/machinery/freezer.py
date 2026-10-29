# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
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
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import ItemPipeSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdatePowerBar, UpdateProgress

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
FLUID_PATH = MAIN_PATH / "fluid_disp"
# 产物分段按钮 mode_btn_0 … mode_btn_4, 选中项显示为按下态
MODE_BTN_NAME = "mode_btn_%d"
MODE_SELECTED_TEXTURE = "textures/ui/button_pressed"
MODE_NORMAL_TEXTURE = "textures/ui/button_default"


@RegistToolDeltaScreen("FreezerUI.main", is_proxy=True)
class FreezerUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.fluid_display = self.GetElement(FLUID_PATH)
        self.mode_btns = []
        for mode in range(len(recipes)):
            btn = self.GetElement(MAIN_PATH / (MODE_BTN_NAME % mode)).asButton()
            btn.SetCallback(lambda _, mode=mode: self.changeMode(mode))
            output_item = recipes.recipes_mapping[mode].outputs["item"][0].id
            btn["item"].asItemRenderer().SetUiItem(Item(output_item))
            self.mode_btns.append(btn)
        self.shown_mode = None
        self.fluid_displayer = FluidDisplayer(self.fluid_display)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )
        self.freezer_mode = None

    def OnTicking(self):
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(tuple(self.pos[1:]))
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0.0)
        self.freezer_mode = GetValue(data, K_MODE, 0)
        fluid = FluidSlotClient(data)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateProgress(self.progress, progress)
        if self.freezer_mode != self.shown_mode:
            self.shown_mode = self.freezer_mode
            for mode, btn in enumerate(self.mode_btns):
                btn["default"].asImage().SetSprite(
                    MODE_SELECTED_TEXTURE if mode == self.freezer_mode else MODE_NORMAL_TEXTURE
                )

    def changeMode(self, mode):
        # type: (int) -> None
        if self.freezer_mode is None or mode == self.freezer_mode:
            return
        _, x, y, z = self.pos
        FreezerModeChangedEvent(x, y, z, mode).send()
