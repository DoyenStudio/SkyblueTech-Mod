# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    K_PROGRESS,
)
from skybluetech_scripts.skybluetech.common.machinery_def.sawmill import (
    STORE_RF_MAX,
    recipes,
)
from ..machinery_extra_pages import CableSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MachinePanelUIProxyEx, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"


@RegistToolDeltaScreen("SawmillUI.main", is_proxy=True)
class SawmillUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_PROGRESS, 0.0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
