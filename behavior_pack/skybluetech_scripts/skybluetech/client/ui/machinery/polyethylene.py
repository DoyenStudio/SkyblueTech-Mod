# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from ....common.define.flags import DEACTIVE_FLAG_FLUID_NOT_MATCH, DEACTIVE_FLAG_OUTPUT_FULL
from ....common.machinery_def import thermal_cracker, small_chemical_reactor
from ....common.machinery_def.basic import K_PROGRESS, K_STORE_RF, K_HEAT_VALUE, FluidSlotClient
from ..machinery_extra_pages import FluidPipeSettingsPage
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdatePowerBar, UpdateProgress, SetHoverText, FormatKelvin


class ChemicalFluidUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPage,)
    definition = None
    thermal = False

    def OnCreate(self):
        self.tanks = dict((i, FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % i))))
                          for i in self.definition.FLUID_SLOT_MAX_VOLUMES)
        self.meter = self.GetElement(MAIN_PATH / ("temperature" if self.thermal else "power_bar"))
        self.progress = self.GetElement(MAIN_PATH / "progress")
        AsRecipeCheckerBtn(self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), self.definition.recipes)

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        for slot, display in self.tanks.items():
            fluid = FluidSlotClient(data, slot)
            display.update(fluid.fluid_id, fluid.volume, self.definition.FLUID_SLOT_MAX_VOLUMES[slot])
        if self.thermal:
            temperature = GetValue(data, K_HEAT_VALUE, 300.0)
            UpdateProgress(self.meter, max(0.0, min(1.0, (temperature - 300.0) / 1100.0)))
            SetHoverText(self.meter, "%s\n1000 K < T ≤ 1300 K；1100 K 满速\n红外热源建议 1200 K\n左侧抽乙烯；右侧抽纯甲烷" % FormatKelvin(temperature))
            # Continuous processing has no batch progress; hide the animated fill.
            UpdateProgress(self.progress, 0)
        else:
            UpdatePowerBar(self.meter, GetValue(data, K_STORE_RF, 0), self.definition.STORE_RF_MAX)
            UpdateProgress(self.progress, GetValue(data, K_PROGRESS, 0))


@RegistToolDeltaScreen("ThermalCrackerUI.main", is_proxy=True)
class ThermalCrackerUI(ChemicalFluidUI):
    definition = thermal_cracker
    thermal = True
    STATUS_RINGS = {DEACTIVE_FLAG_FLUID_NOT_MATCH: ("ring_tout_",)}


@RegistToolDeltaScreen("SmallChemicalReactorUI.main", is_proxy=True)
class SmallChemicalReactorUI(ChemicalFluidUI):
    definition = small_chemical_reactor
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_tout_", "ring_out_")}
