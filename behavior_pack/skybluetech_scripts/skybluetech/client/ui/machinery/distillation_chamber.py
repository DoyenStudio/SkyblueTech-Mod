# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_HEAT_VALUE,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.distillation_chamber import (
    INPUT_MAX_VOLUME,
    K_OUTPUT_RATE,
    OUTPUT_MAX_VOLUME,
    recipes,
)
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import PipeSettingsPageIndirectional
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, FormatFluidVolume, FormatKelvin

TEMPERATURE_PATH = MAIN_PATH / "right_board/temp_disp"
RATE_PATH = MAIN_PATH / "right_board/rate_disp"
LOWER_FLUID_PATH = MAIN_PATH / "lower_fluid"
UPPER_FLUID_PATH = MAIN_PATH / "upper_fluid"


@RegistToolDeltaScreen("DistillationChamberUI.main", is_proxy=True)
class DistillationChamberUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.upper_fluid = self.GetElement(UPPER_FLUID_PATH)
        self.lower_fluid = self.GetElement(LOWER_FLUID_PATH)
        self.temperature_label = self.GetElement(TEMPERATURE_PATH).asLabel()
        self.rate_label = self.GetElement(RATE_PATH).asLabel()
        self.fluid_displayer1 = FluidDisplayer(self.lower_fluid)
        self.fluid_displayer2 = FluidDisplayer(self.upper_fluid)
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        input_fluid = FluidSlotClient(data, 0)
        output_fluid = FluidSlotClient(data, 1)
        output_rate = GetValue(data, K_OUTPUT_RATE, 0)
        current_temperature = Thermal.GetKelvin(
            GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT)
        )
        self.fluid_displayer1.update(
            input_fluid.fluid_id, input_fluid.volume, INPUT_MAX_VOLUME
        )
        self.fluid_displayer2.update(
            output_fluid.fluid_id, output_fluid.volume, OUTPUT_MAX_VOLUME
        )
        self.rate_label.SetText(FormatFluidVolume(output_rate) + "/s")
        self.temperature_label.SetText(FormatKelvin(current_temperature))
