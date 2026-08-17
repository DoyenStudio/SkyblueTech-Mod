# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    K_PROGRESS,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.precision_cutter import (
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
    recipes,
)
from ..machinery_extra_pages import CableSettingsPage, PipeSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MachinePanelUIProxyEx, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressL2R, FluidDisplayer


POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
FLUID_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("PrecisionCutterUI.main", is_proxy=True)
class PrecisionCutterUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage, PipeSettingsPage)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))
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
        progress = GetValue(data, K_PROGRESS, 0)
        fluid = FluidSlotClient(data)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)
