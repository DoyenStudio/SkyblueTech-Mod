# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.reacting_thermal_generator import (
    MAX_FLUID_VOLUMES,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import (
    CableSettingsPage,
    PipeSettingsPage,
)
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdateGenericProgressL2R, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
PRGS_PATH = MAIN_PATH / "progress"
INPUT_FLUID_PATH = MAIN_PATH / "input_fluid_display"
OUTPUT_FLUID_PATH = MAIN_PATH / "output_fluid_display"


@RegistToolDeltaScreen("ReactingThermalGeneratorUI.main", is_proxy=True)
class ReactingThermalGeneratorUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        CableSettingsPage,
        PipeSettingsPage,
    )

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.progress = self.GetElement(PRGS_PATH)
        self.input_fluid_displayer = FluidDisplayer(self.GetElement(INPUT_FLUID_PATH))
        self.output_fluid_displayer = FluidDisplayer(self.GetElement(OUTPUT_FLUID_PATH))
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
        input_fluid = FluidSlotClient(data, 0)
        output_fluid = FluidSlotClient(data, 1)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressL2R(self.progress, progress)
        self.input_fluid_displayer.update(
            input_fluid.fluid_id, input_fluid.volume, MAX_FLUID_VOLUMES[0]
        )
        self.output_fluid_displayer.update(
            output_fluid.fluid_id, output_fluid.volume, MAX_FLUID_VOLUMES[1]
        )
