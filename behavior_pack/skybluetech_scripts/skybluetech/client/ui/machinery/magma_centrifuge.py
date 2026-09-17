# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.magma_centrifuge import (
    FLUID_SLOT_MAX_VOLUMES,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import PipeSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdateGenericProgressL2R, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
LEFT_FLUID = MAIN_PATH / "left_fluid"
RIGHT_FLUID = MAIN_PATH / "right_fluid"


@RegistToolDeltaScreen("MagmaCentrifugeUI.main", is_proxy=True)
class MagmaCentrifugeUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.left_fluid_displayer = FluidDisplayer(self.GetElement(LEFT_FLUID))
        self.right_fluid_displayers = [
            FluidDisplayer(self.GetElement(RIGHT_FLUID + str(i + 1))) for i in range(6)
        ]
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
        left_fluid = FluidSlotClient(data, 0)
        right_fluids = [FluidSlotClient(data, i) for i in range(1, 7)]
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        self.left_fluid_displayer.update(
            left_fluid.fluid_id, left_fluid.volume, FLUID_SLOT_MAX_VOLUMES[0]
        )
        for i in range(6):
            self.right_fluid_displayers[i].update(
                right_fluids[i].fluid_id,
                right_fluids[i].volume,
                FLUID_SLOT_MAX_VOLUMES[i + 1],
            )
