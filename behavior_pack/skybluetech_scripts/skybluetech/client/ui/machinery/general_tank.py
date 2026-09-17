# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_FLUID_ID,
    K_FLUID_VOLUME,
)
from skybluetech_scripts.skybluetech.common.machinery_def.tank import TANK_MAX_VOLUMES
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData, GetBlockName
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import PipeSettingsPageIndirectional
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer

FLUID_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("GeneralTankUI.main", is_proxy=True)
class GeneralTankUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPageIndirectional,)

    def OnCreate(self):
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))

    def OnTicking(self):
        block_id = GetBlockName(self.pos[1:])
        if not block_id:
            return
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        fluid_id = GetValue(data, K_FLUID_ID, None)
        fluid_volume = GetValue(data, K_FLUID_VOLUME, 0)
        max_fluid_volume = TANK_MAX_VOLUMES.get(block_id, 1.0)
        self.fluid_displayer.update(fluid_id, fluid_volume, max_fluid_volume)
