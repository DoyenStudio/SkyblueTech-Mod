# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    FluidSlotClient,
)
from skybluetech_scripts.skybluetech.common.machinery_def.geothermal_generator import (
    K_BURN_TICKS_LEFT,
    MAX_LAVA_VOLUME,
    MAX_WATER_VOLUME,
    ONCE_BURNING_TICKS,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import (
    CableSettingsPageIndirectional,
    PipeSettingsPageIndirectional,
)
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FluidDisplayer, UpdateFlame, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
FLUID_LAVA_PATH = MAIN_PATH / "lava_display"
FLUID_WATER_PATH = MAIN_PATH / "water_display"
FLAME_PATH = MAIN_PATH / "flame"


@RegistToolDeltaScreen("GeoThermalGeneratorUI.main", is_proxy=True)
class GeoThermalGeneratorUI(MachinePanelUIProxyEx):
    available_extra_pages = (
        CableSettingsPageIndirectional,
        PipeSettingsPageIndirectional,
    )

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.lava_display = self.GetElement(FLUID_LAVA_PATH)
        self.water_display = self.GetElement(FLUID_WATER_PATH)
        self.flame = self.GetElement(FLAME_PATH)
        self.lava_displayer = FluidDisplayer(self.lava_display)
        self.water_displayer = FluidDisplayer(self.water_display)

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        lava_fluid = FluidSlotClient(data, 0)
        water_fluid = FluidSlotClient(data, 1)
        store_rf = GetValue(data, K_STORE_RF, 0)
        progress = GetValue(data, K_BURN_TICKS_LEFT, 0) * 1.0 / ONCE_BURNING_TICKS
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateFlame(self.flame, progress)
        self.lava_displayer.update(
            lava_fluid.fluid_id, lava_fluid.volume, MAX_LAVA_VOLUME
        )
        self.water_displayer.update(
            water_fluid.fluid_id, water_fluid.volume, MAX_WATER_VOLUME
        )
