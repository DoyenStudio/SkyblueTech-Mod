# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.define.flags import (
    DEACTIVE_FLAG_FLUID_NOT_MATCH,
    DEACTIVE_FLAG_OUTPUT_FULL,
)
from skybluetech_scripts.skybluetech.common.machinery_def import thermal_cracker
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_HEAT_VALUE,
    FluidSlotClient,
)

from ..machinery_extra_pages import (
    FluidOutputSettingsPage,
    FluidPipeSettingsPage,
    ItemPipeSettingsPage,
)
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdateProgress, SetHoverText, FormatKelvin


@RegistToolDeltaScreen("ThermalCrackerUI.main", is_proxy=True)
class ThermalCrackerUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPage, FluidPipeSettingsPage, FluidOutputSettingsPage)
    fluid_output_slot_paths = {2: "fluid2", 3: "fluid3"}
    definition = thermal_cracker
    STATUS_RINGS = {
        DEACTIVE_FLAG_FLUID_NOT_MATCH: ("ring_tout_",),
        DEACTIVE_FLAG_OUTPUT_FULL: ("ring_out_", "ring_tout_"),
    }

    def OnCreate(self):
        self.tanks = dict(
            (i, FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % i))))
            for i in self.definition.FLUID_SLOT_MAX_VOLUMES
        )
        self.meter = self.GetElement(MAIN_PATH / "temperature")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        self.full_speed_temperature = max(
            recipe.fit_temperature for recipe in self.definition.recipes
        )
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            self.definition.recipes,
        )

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        for slot, display in self.tanks.items():
            fluid = FluidSlotClient(data, slot)
            display.update(
                fluid.fluid_id,
                fluid.volume,
                self.definition.FLUID_SLOT_MAX_VOLUMES[slot],
            )
        temperature = GetValue(data, K_HEAT_VALUE, 300.0)
        UpdateProgress(self.meter, (temperature - 300.0) / (self.full_speed_temperature - 300.0))
        SetHoverText(self.meter, FormatKelvin(temperature) + "\n§7外部供热；温区与热耗见配方")
        UpdateProgress(self.progress, GetValue(data, self.definition.K_BATCH_PROGRESS, 0.0))
