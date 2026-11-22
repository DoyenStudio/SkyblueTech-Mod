# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.define.flags import DEACTIVE_FLAG_OUTPUT_FULL
from skybluetech_scripts.skybluetech.common.machinery_def import high_temp_electrolyzer as definition
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotClient, K_HEAT_VALUE, K_PROGRESS, K_STORE_RF
from skybluetech_scripts.skybluetech.client.ui.machinery_extra_pages import (
    FluidPipeSettingsPage, ItemPipeSettingsPage,
)
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import AsRecipeCheckerBtn
from skybluetech_scripts.skybluetech.client.ui.machinery.define_ex import MAIN_PATH, MachinePanelUIProxyEx
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FluidDisplayer, UpdatePowerBar, UpdateProgress


@RegistToolDeltaScreen("HighTempElectrolyzerUI.main", is_proxy=True)
class HighTempElectrolyzerUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPage, FluidPipeSettingsPage)
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_out_", "ring_tout_")}

    def OnCreate(self):
        self.tanks = {slot: FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot)))
                      for slot in definition.FLUID_SLOT_MAX_VOLUMES}
        self.temperature = self.GetElement(MAIN_PATH / "temperature").asLabel()
        self.power_bar = self.GetElement(MAIN_PATH / "power_bar")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        AsRecipeCheckerBtn(self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(), definition.recipes)

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        for slot, displayer in self.tanks.items():
            fluid = FluidSlotClient(data, slot)
            displayer.update(fluid.fluid_id, fluid.volume, definition.FLUID_SLOT_MAX_VOLUMES[slot])
        self.temperature.SetText("%d K" % GetValue(data, K_HEAT_VALUE, 300))
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), definition.STORE_RF_MAX)
        UpdateProgress(self.progress, GetValue(data, K_PROGRESS, 0))
