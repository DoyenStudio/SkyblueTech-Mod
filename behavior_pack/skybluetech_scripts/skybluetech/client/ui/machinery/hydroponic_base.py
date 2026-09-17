# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import FluidSlotClient
from skybluetech_scripts.skybluetech.common.machinery_def.hydroponic_base import (
    FLUID_0_MAX_VOLUME,
    FLUID_1_MAX_VOLUME,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen

from ..machinery_extra_pages import (
    CableSettingsPageIndirectional,
    PipeSettingsPageIndirectional,
)
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer

FLUID_0_PATH = MAIN_PATH / "fluid0"
FLUID_1_PATH = MAIN_PATH / "fluid1"


@RegistToolDeltaScreen("HydroponicBaseUI.main", is_proxy=True)
class HydroponicBaseUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        CableSettingsPageIndirectional,
        PipeSettingsPageIndirectional,
    )

    def OnCreate(self):
        self.fluid_0 = self.GetElement(FLUID_0_PATH)
        self.fluid_1 = self.GetElement(FLUID_1_PATH)
        self.fluid_0_displayer = FluidDisplayer(self.fluid_0)
        self.fluid_1_displayer = FluidDisplayer(self.fluid_1)

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        fluid_0 = FluidSlotClient(data, 0)
        fluid_1 = FluidSlotClient(data, 1)
        self.fluid_0_displayer.update(
            fluid_0.fluid_id, fluid_0.volume, FLUID_0_MAX_VOLUME
        )
        self.fluid_1_displayer.update(
            fluid_1.fluid_id, fluid_1.volume, FLUID_1_MAX_VOLUME
        )
