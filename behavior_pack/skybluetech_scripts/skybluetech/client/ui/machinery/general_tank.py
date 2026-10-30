# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.tank import TANK_MAX_VOLUMES
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen

from ..machinery_extra_pages import FluidPipeSettingsPageIndirectional
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer

FLUID_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("GeneralTankUI.main", is_proxy=True)
class GeneralTankUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))

    def OnTicking(self):
        block_id = (CF.CreateBlockInfo(LEVEL_ID).GetBlock(self.pos[1:]) or (None, 0))[0]
        if not block_id:
            return
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        max_volume = TANK_MAX_VOLUMES.get(block_id, 1.0)
        fluid = FluidSlotClient(data, 0, max_volume)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, max_volume)
