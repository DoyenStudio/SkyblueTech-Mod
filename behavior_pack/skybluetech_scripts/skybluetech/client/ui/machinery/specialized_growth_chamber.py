# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.define.flags import DEACTIVE_FLAG_OUTPUT_FULL
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.specialized_growth_chamber import (
    FLUID_SLOT_MAX_VOLUMES,
    POWER_COST,
    STORE_RF_MAX,
    recipes,
)

from ..recipe_checker import AsRecipeCheckerBtn
from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import FluidDisplayer, UpdatePowerBar, UpdateProgress


@RegistToolDeltaScreen("SpecializedGrowthChamberUI.main", is_proxy=True)
class SpecializedGrowthChamberUI(MachinePanelUIProxy):
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_out_", "ring_tout_")}

    def OnCreate(self):
        self.power_bar = self.GetElement(MAIN_PATH / "power_bar")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        self.fluid_displayers = {
            slot: FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot)))
            for slot in FLUID_SLOT_MAX_VOLUMES
        }
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            recipes,
        )

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        UpdatePowerBar(
            self.power_bar,
            store_rf,
            STORE_RF_MAX,
            hover="§b储能： §f%d / %d RF\n§7固定功耗： §f%d RF/t"
            % (store_rf, STORE_RF_MAX, POWER_COST),
        )
        UpdateProgress(self.progress, GetValue(data, K_PROGRESS, 0))
        for slot, displayer in self.fluid_displayers.items():
            fluid = FluidSlotClient(data, slot)
            displayer.update(
                fluid.fluid_id, fluid.volume, FLUID_SLOT_MAX_VOLUMES[slot]
            )
