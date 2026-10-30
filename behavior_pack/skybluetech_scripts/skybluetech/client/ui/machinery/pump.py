# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    FluidSlotClient,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.pump import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import FluidPipeSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_PATH = MAIN_PATH / "fluid_display"


@RegistToolDeltaScreen("PumpUI.main", is_proxy=True)
class PumpUI(MachinePanelUIProxyEx):
    available_extra_pages = (FluidPipeSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.fluid_displayer = FluidDisplayer(self.GetElement(FLUID_PATH))

    def OnTicking(self):
        data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        fluid = FluidSlotClient(data, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        self.fluid_displayer.update(fluid.fluid_id, fluid.volume, MAX_FLUID_VOLUME)
