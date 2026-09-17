# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.gas_burning_generator import (
    MAX_INPUT_GAS_VOLUME,
    MAX_OUTPUT_GAS_VOLUME,
    STORE_RF_MAX,
    recipes,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import PipeSettingsPageIndirectional
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdateFlame, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
GAS_INPUT_PATH = MAIN_PATH / "gas_input"
GAS_OUTPUT_PATH = MAIN_PATH / "gas_output"
FLAME_PATH = MAIN_PATH / "flame"


@RegistToolDeltaScreen("GasBurningGeneratorUI.main", is_proxy=True)
class GasBurningGeneratorUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.gas_input = self.GetElement(GAS_INPUT_PATH)
        self.gas_output = self.GetElement(GAS_OUTPUT_PATH)
        self.flame = self.GetElement(FLAME_PATH)
        self.input_gas_displayer = FluidDisplayer(self.gas_input)
        self.output_gas_displayer = FluidDisplayer(self.gas_output)
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
        input_gas = FluidSlotClient(data, 0)
        output_gas = FluidSlotClient(data, 1)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateFlame(self.flame, input_gas.volume * 1.0 / MAX_INPUT_GAS_VOLUME)
        self.input_gas_displayer.update(
            input_gas.fluid_id, input_gas.volume, MAX_INPUT_GAS_VOLUME
        )
        self.output_gas_displayer.update(
            output_gas.fluid_id, output_gas.volume, MAX_OUTPUT_GAS_VOLUME
        )
