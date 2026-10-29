# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.skybluetech.common.machinery_def.fluid_interface import FLUID_INTERFACE_MAX_VOLUME

from ..machinery_extra_pages import FluidPipeSettingsPageIndirectional
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer

FLUID_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("FluidInputInterfaceUI.main", is_proxy=True)
class FluidInputInterfaceUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.fluid_display = self.GetElement(FLUID_PATH)
        self.fluid_updater = FluidDisplayer(self.fluid_display)

    def OnTicking(self):
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(tuple(self.pos[1:]))
        if data is None:
            return
        data = data["exData"]
        fluid = FluidSlotClient(data, 0)
        self.fluid_updater.update(fluid.fluid_id, fluid.volume, FLUID_INTERFACE_MAX_VOLUME)
