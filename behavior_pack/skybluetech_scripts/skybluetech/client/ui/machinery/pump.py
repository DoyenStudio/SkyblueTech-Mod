# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_FLUID_ID,
    K_FLUID_VOLUME,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.pump import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import PipeSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("PumpUI.main", is_proxy=True)
class PumpUI(MachinePanelUIProxyEx):
    available_extra_pages = (PipeSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        fluid_id = GetValue(data, K_FLUID_ID, None)
        fluid_volume = GetValue(data, K_FLUID_VOLUME, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        self.fluid_displayer.update(fluid_id, fluid_volume, MAX_FLUID_VOLUME)
