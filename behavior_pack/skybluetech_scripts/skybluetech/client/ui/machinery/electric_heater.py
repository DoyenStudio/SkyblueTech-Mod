# coding=utf-8
from skybluetech_scripts.skybluetech.common.events.machinery.electric_heater import (
    ElectricHeaterSubmitModifiesEvent,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_HEAT_VALUE,
    K_STORE_RF,
)
from skybluetech_scripts.skybluetech.common.machinery_def.electric_heater import (
    K_CURRENT_POWER,
    K_KELVIN_LIMIT,
    K_MAX_POWER,
    MAX_KELVIN,
    MAX_POWER,
    MIN_KELVIN,
    STORE_RF_MAX,
)
from skybluetech_scripts.skybluetech.common.utils.phys_math import Thermal
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import Binder, RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue

from .define import MAIN_PATH, MachinePanelUIProxy
from .utils import UpdatePowerBar

POWER_BAR_PATH = MAIN_PATH / "power_bar"
DATABAR_TEXT_PATH = MAIN_PATH / "databar/text"
POWER_INPUT_PATH = MAIN_PATH / "power_input"
KELVIN_LIMIT_INPUT_PATH = MAIN_PATH / "kelvin_limit_input"
CONFIRM_BTN_PATH = MAIN_PATH / "confirm_btn"

# 与 ElectricHeaterUI.json 里两个编辑框的 $text_box_name 保持一致
POWER_BOX_NAME = "#electric_heater.power"
KELVIN_LIMIT_BOX_NAME = "#electric_heater.kelvin_limit"


@RegistToolDeltaScreen("ElectricHeaterUI.main", is_proxy=True)
class ElectricHeaterUI(MachinePanelUIProxy):
    def OnCreate(self):
        _, x, y, z = self.pos
        self.power_bar = self.GetElement(POWER_BAR_PATH)
        self.databar_text = self.GetElement(DATABAR_TEXT_PATH).asLabel()
        self.power_input = self.GetElement(POWER_INPUT_PATH).asTextEditBox()
        self.kelvin_limit_input = self.GetElement(
            KELVIN_LIMIT_INPUT_PATH
        ).asTextEditBox()
        self.confirm_btn = (
            self.GetElement(CONFIRM_BTN_PATH).asButton().SetCallback(self.onSubmit)
        )
        block_nbt = GetBlockEntityData(x, y, z)
        if block_nbt is None:
            return
        ex_data = block_nbt.get("exData")
        if ex_data is None:
            return
        # 最大功率为 0 / 设定温度等于下限(环境温度) 说明玩家从没设过, 让输入框保持空白
        max_power = GetValue(ex_data, K_MAX_POWER, 0)
        self.power_input.SetText(str(int(max_power)) if max_power else "")
        kelvin_limit = GetValue(ex_data, K_KELVIN_LIMIT, MIN_KELVIN)
        if kelvin_limit != MIN_KELVIN:
            self.kelvin_limit_input.SetText(str(int(kelvin_limit)))
        else:
            self.kelvin_limit_input.SetText("")

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        current_temperature = Thermal.GetKelvin(
            GetValue(data, K_HEAT_VALUE, Thermal.ENV_HEAT)
        )
        kelvin_limit = GetValue(data, K_KELVIN_LIMIT, MIN_KELVIN)
        current_power = GetValue(data, K_CURRENT_POWER, 0.0)
        UpdatePowerBar(self.power_bar, GetValue(data, K_STORE_RF, 0), STORE_RF_MAX)
        self.databar_text.SetText(
            "当前温度： %.1f K\n设定温度： %.1f K\n当前功率： %.1f RF/t\n"
            % (current_temperature, kelvin_limit, current_power)
        )

    def onSubmit(self, _):
        power_str = self.power_input.GetText()
        kelvin_limit_str = self.kelvin_limit_input.GetText()
        if power_str == "" or kelvin_limit_str == "":
            return
        _, x, y, z = self.pos
        ElectricHeaterSubmitModifiesEvent(
            x, y, z, int(power_str), int(kelvin_limit_str)
        ).send()

    @Binder.binding(Binder.BF_EditFinished, POWER_BOX_NAME)
    def onPowerEdited(self, params):
        text = params["Text"]
        if text == "":
            return
        try:
            value = int(float(text))
        except ValueError:
            self.power_input.SetText("")
            return
        # 夹紧到本机能力范围: 最大功率不能为负, 也不能超过储电上限支持的值
        self.power_input.SetText(str(min(max(value, 0), MAX_POWER)))

    @Binder.binding(Binder.BF_EditFinished, KELVIN_LIMIT_BOX_NAME)
    def onKelvinLimitEdited(self, params):
        text = params["Text"]
        if text == "":
            return
        try:
            value = int(float(text))
        except ValueError:
            self.kelvin_limit_input.SetText("")
            return
        # 夹紧到本机能力范围: 低于环境温度没意义, 高于 MAX_KELVIN 永远到不了
        self.kelvin_limit_input.SetText(str(min(max(value, MIN_KELVIN), MAX_KELVIN)))
