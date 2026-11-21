# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.oilfuel_generator import (
    MAX_INPUT_FUEL_VOLUME,
    STORE_RF_MAX,
    recipes,
)

from ..machinery_extra_pages import FluidPipeSettingsPageIndirectional
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdatePowerBar


@RegistToolDeltaScreen("OilFuelGeneratorUI.main", is_proxy=True)
class OilFuelGeneratorUI(MachinePanelUIProxyEx):
    IS_GENERATOR = True
    available_extra_pages = (FluidPipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.power_bar = self.GetElement(MAIN_PATH / "power_bar")
        self.fuel_displayer = FluidDisplayer(self.GetElement(MAIN_PATH / "fuel_input"))
        AsRecipeCheckerBtn(self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), recipes)

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        fuel = FluidSlotClient(data, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        self.fuel_displayer.update(fuel.fluid_id, fuel.volume, MAX_INPUT_FUEL_VOLUME)
