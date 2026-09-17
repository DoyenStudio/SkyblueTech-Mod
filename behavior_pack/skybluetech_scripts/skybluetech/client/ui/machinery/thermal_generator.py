# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.thermal_generator import (
    K_BURN_SEC_LEFT,
    K_MAX_BURN_SEC,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from ..machinery_extra_pages import CableSettingsPage
from .define_ex import MAIN_PATH, MachinePanelUIProxyEx
from .utils import UpdateFlame, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
FLAME_PATH = MAIN_PATH / "flame"


@RegistToolDeltaScreen("ThermalGeneratorUI.main", is_proxy=True)
class ThermalGeneratorUI(MachinePanelUIProxyEx):
    available_extra_pages = (CableSettingsPage,)

    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.flame = self.GetElement(FLAME_PATH)

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        burn_seconds_left = GetValue(data, K_BURN_SEC_LEFT, 0)
        max_burn_seconds = GetValue(data, K_MAX_BURN_SEC, 1)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateFlame(self.flame, float(burn_seconds_left) / max_burn_seconds)
