# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotClient
from skybluetech_scripts.skybluetech.common.machinery_def.specialized_growth_base import (
    FLUID_SLOT_MAX_VOLUMES,
)

from ..machinery_extra_pages import (
    ItemPipeSettingsPageIndirectional,
    FluidPipeSettingsPageIndirectional,
)
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer


@RegistToolDeltaScreen("SpecializedGrowthBaseUI.main", is_proxy=True)
class SpecializedGrowthBaseUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        ItemPipeSettingsPageIndirectional,
        FluidPipeSettingsPageIndirectional,
    )

    def OnCreate(self):
        self.fluid_displayers = {
            slot: FluidDisplayer(self.GetElement(MAIN_PATH / ("fluid%d" % slot)))
            for slot in FLUID_SLOT_MAX_VOLUMES
        }

    def OnTicking(self):
        block = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block is None or block.get("exData") is None:
            return
        data = block["exData"]
        for slot, displayer in self.fluid_displayers.items():
            fluid = FluidSlotClient(data, slot)
            displayer.update(
                fluid.fluid_id, fluid.volume, FLUID_SLOT_MAX_VOLUMES[slot]
            )
