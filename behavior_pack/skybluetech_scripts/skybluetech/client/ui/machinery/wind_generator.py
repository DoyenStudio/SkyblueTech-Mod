# coding=utf-8
from skybluetech_scripts.skybluetech.common.machinery_def.basic import K_STORE_RF
from skybluetech_scripts.skybluetech.common.machinery_def.wind_generator import (
    K_MCW,
    K_OUTPUT_POWER,
    STORE_RF_MAX,
)
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
TEXT_PATH = MAIN_PATH / "text"


@RegistToolDeltaScreen("WindGeneratorUI.main", is_proxy=True)
class WindGeneratorUI(MachinePanelUIProxy):
    def OnCreate(self):
        self.power_bar = self.GetElement(POWER_PATH)
        self.text = self.GetElement(TEXT_PATH).asLabel()

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        store_rf = GetValue(data, K_STORE_RF, 0)
        mcw = GetValue(data, K_MCW, 0)
        output_power = GetValue(data, K_OUTPUT_POWER, 0)
        UpdatePowerBar(self.power_bar, store_rf, STORE_RF_MAX)
        self.text.SetText("风强度: %d MCW\n输出功率: %d RF/t" % (mcw, output_power))
