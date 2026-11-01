# coding=utf-8
from skybluetech_scripts.tooldelta.cli import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_HEAT_VALUE
from skybluetech_scripts.skybluetech.common.machinery_def.fuel_heater import (
    K_BURN_SEC_LEFT,
    K_MAX_BURN_SEC,
    MAX_KELVIN,
    MIN_KELVIN,
)
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal

from ..machinery_extra_pages import ItemPipeSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import FormatKelvin, SetHoverText, UpdateFlame, UpdateProgress

TEMPERATURE_LABEL_PATH = MAIN_PATH / "temperature_label"
TEMPERATURE_PATH = MAIN_PATH / "temperature"
FLAME_PATH = MAIN_PATH / "flame"


@RegistToolDeltaScreen("FuelHeaterUI.main", is_proxy=True)
class FuelHeaterUI(MachinePanelUIProxyEx):
    available_extra_pages = (ItemPipeSettingsPage,)

    def OnCreate(self):
        self.temperature_label = self.GetElement(TEMPERATURE_LABEL_PATH).asLabel()
        self.temperature = self.GetElement(TEMPERATURE_PATH)
        self.last_temperature_ratio = None
        self.flame = self.GetElement(FLAME_PATH)

    def OnTicking(self):
        block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(self.pos[1:])
        if block_data is None:
            return
        data = block_data.get("exData")
        if data is None:
            return
        current_temperature = Thermal.GetKelvin(
            GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT)
        )
        temperature_text = FormatKelvin(current_temperature)
        self.temperature_label.SetText(temperature_text)
        SetHoverText(self.temperature, temperature_text)
        temperature_ratio = max(
            0.0,
            min(
                1.0,
                (current_temperature - MIN_KELVIN) / float(MAX_KELVIN - MIN_KELVIN),
            ),
        )
        if temperature_ratio != self.last_temperature_ratio:
            UpdateProgress(self.temperature, temperature_ratio)
            self.last_temperature_ratio = temperature_ratio
        burn_seconds_left = GetValue(data, K_BURN_SEC_LEFT, 0.0)
        max_burn_seconds = GetValue(data, K_MAX_BURN_SEC, 1.0)
        if max_burn_seconds <= 0.0:
            max_burn_seconds = 1.0
        UpdateFlame(
            self.flame, max(0.0, min(1.0, float(burn_seconds_left) / max_burn_seconds))
        )
