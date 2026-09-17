# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.alloy_furnace import (
    RF_MAX,
    recipes,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import UpdateFlame, UpdateGenericProgressL2R, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "/progress"
FLAME_PATH = MAIN_PATH / "flame"


@RegistToolDeltaScreen("AlloyFurnaceUI.main", is_proxy=True)
class AlloyFurnaceUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.flame = self.GetElement(FLAME_PATH)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        storage_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0)
        UpdatePowerBar(self.power_bar, storage_rf, RF_MAX)
        UpdateFlame(self.flame, float(storage_rf) / RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
