# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.define.flags import DEACTIVE_FLAG_OUTPUT_FULL
from skybluetech_scripts.skybluetech.common.machinery_def import industrial_centrifuge
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_HEAT_VALUE,
    K_PROGRESS,
    K_STORE_RF,
    FluidSlotClient,
)

from ..machinery_extra_pages import (
    FluidPipeSettingsPage,
    FluidOutputSettingsPage,
    ItemPipeSettingsPage,
)
from ..recipe_checker import AsRecipeCheckerBtn
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FormatKelvin, FluidDisplayer, UpdatePowerBar, UpdateProgress


@RegistToolDeltaScreen("IndustrialCentrifugeUI.main", is_proxy=True)
class IndustrialCentrifugeUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        ItemPipeSettingsPage,
        FluidPipeSettingsPage,
        FluidOutputSettingsPage,
    )
    fluid_output_slot_paths = {1: "fluid1", 2: "fluid2"}
    STATUS_RINGS = {DEACTIVE_FLAG_OUTPUT_FULL: ("ring_tout_", "ring_out_")}

    def OnCreate(self):
        self.tanks = dict(
            (slot, FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot))))
            for slot in industrial_centrifuge.FLUID_SLOT_MAX_VOLUMES
        )
        self.temperature = self.GetElement(MAIN_PATH / "temperature").asLabel()
        self.meter = self.GetElement(MAIN_PATH / "power_bar")
        self.progress = self.GetElement(MAIN_PATH / "progress")
        AsRecipeCheckerBtn(
            self.GetElement(MAIN_PATH / "recipe_check_btn").asButton(),
            industrial_centrifuge.recipes,
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
                industrial_centrifuge.FLUID_SLOT_MAX_VOLUMES[slot],
            )
        UpdatePowerBar(
            self.meter, GetValue(data, K_STORE_RF, 0), industrial_centrifuge.STORE_RF_MAX
        )
        self.temperature.SetText(FormatKelvin(GetValue(data, K_HEAT_VALUE, 300)))
        UpdateProgress(self.progress, GetValue(data, K_PROGRESS, 0))
