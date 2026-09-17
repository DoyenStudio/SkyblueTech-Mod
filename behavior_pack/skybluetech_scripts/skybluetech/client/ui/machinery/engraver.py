# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.engraver import (
    FLUID_SLOT_MAX_VOLUMES,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPage, PipeSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import (
    FluidDisplayer,
    UpdateGenericProgressL2R,
    UpdatePowerBar,
)

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
# 面板上这两个控件命名为 fluid1 / fluid2, 分别显示机器的流体槽位 0 / 1
FLUID_0_PATH = MAIN_PATH / "fluid1"
FLUID_1_PATH = MAIN_PATH / "fluid2"


@RegistToolDeltaScreen("EngraverUI.main", is_proxy=True)
class EngraverUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        CableSettingsPage,
        PipeSettingsPage,
    )

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.fluid_0_displayer = FluidDisplayer(self.GetElement(FLUID_0_PATH))
        self.fluid_1_displayer = FluidDisplayer(self.GetElement(FLUID_1_PATH))
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
        fluid_0 = FluidSlotClient(data, 0)
        fluid_1 = FluidSlotClient(data, 1)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        self.fluid_0_displayer.update(
            fluid_0.fluid_id, fluid_0.volume, FLUID_SLOT_MAX_VOLUMES[0]
        )
        self.fluid_1_displayer.update(
            fluid_1.fluid_id, fluid_1.volume, FLUID_SLOT_MAX_VOLUMES[1]
        )
