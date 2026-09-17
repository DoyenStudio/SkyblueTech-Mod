# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.solar_panel import (
    K_LIGHT_LEVEL,
    K_OUTPUT_POWER,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import UpdateGenericProgressT2B, UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
SUN_PATH = MAIN_PATH / "progress"
TEXT_PATH = MAIN_PATH / "text"


@RegistToolDeltaScreen("SolarPanelUI.main", is_proxy=True)
class SolarPanelUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.sun = self.GetElement(SUN_PATH)
        self.text = self.GetElement(TEXT_PATH).asLabel()

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        light_level = GetValue(data, K_LIGHT_LEVEL, 0)
        output_power = GetValue(data, K_OUTPUT_POWER, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        UpdateGenericProgressT2B(self.sun, float(light_level) / 15)
        self.text.SetText(
            "太阳光强度: %d MCLux\n电池板输出功率: %d RF/t"
            % (light_level, output_power)
        )
