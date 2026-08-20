# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetBlockEntityData
from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen, Binder
from skybluetech_scripts.tooldelta.utils.nbt import GetValueWithDefault as GetValue
from skybluetech_scripts.skybluetech.common.events.machinery.electric_heater import (
    ElectricHeaterSubmitModifiesEvent,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic import (
    K_STORE_RF,
    K_HEAT_VALUE,
    ENV_TEMPERATURE,
)
from skybluetech_scripts.skybluetech.common.machinery_def.electric_heater import (
    K_SET_POWER,
    K_KELVIN_LIMIT,
    STORE_RF_MAX,
)
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_PATH = MAIN_PATH / "power_bar"
DATABAR_TEXT_PATH = MAIN_PATH / "databar/text"
POWER_INPUT_PATH = MAIN_PATH / "power_input"
KELVIN_LIMIT_INPUT_PATH = MAIN_PATH / "kelvin_limit_input"
CONFIRM_BTN_PATH = MAIN_PATH / "confirm_btn"


@RegistToolDeltaScreen("ElectricHeaterUI.main", is_proxy=True)
class ElectricHeaterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.power_bar = self.GetElement(POWER_PATH)
        self.databar_text = self.GetElement(DATABAR_TEXT_PATH).asLabel()
        self.power_input = self.GetElement(POWER_INPUT_PATH).asTextEditBox()
        self.kevin_limit_input = self.GetElement(
            KELVIN_LIMIT_INPUT_PATH
        ).asTextEditBox()
        self.confirm_btn = (
            self.GetElement(CONFIRM_BTN_PATH).asButton().SetCallback(self.onSubmit)
        )
        block_nbt = GetBlockEntityData(x, y, z)
        if block_nbt is not None:
            ex_data = block_nbt.get("exData")
            if ex_data is not None:
                current_power = GetValue(ex_data, K_SET_POWER, 0) / 5  # 5 tick 运行一次
                if current_power != 0:
                    self.power_input.SetText(str(current_power))
                else:
                    self.power_input.SetText("")
                current_kelvin_limit = GetValue(ex_data, K_KELVIN_LIMIT, 300)
                if current_kelvin_limit != 300:
                    self.kevin_limit_input.SetText(str(current_kelvin_limit))
                else:
                    self.kevin_limit_input.SetText("")

    def OnTicking(self):
        data = GetBlockEntityData(*self.pos[1:])
        if data is None:
            return
        data = data["exData"]
        storage_rf = GetValue(data, K_STORE_RF, 0)
        power = GetValue(data, K_SET_POWER, 0) / 5  # 5 tick 运行一次
        current_temperature = GetValue(data, K_HEAT_VALUE, 0) + ENV_TEMPERATURE
        UpdatePowerBar(self.power_bar, storage_rf, STORE_RF_MAX)
        self.databar_text.SetText(
            "设定功率： %d RF/t\n当前温度： %.1f°K" % (power, current_temperature)
        )

    def onSubmit(self, _):
        power_str = self.power_input.GetText()
        if power_str == "":
            return
        kelvin_limit_str = self.kevin_limit_input.GetText()
        if kelvin_limit_str == "":
            return
        _, x, y, z = self.pos
        ElectricHeaterSubmitModifiesEvent(
            x, y, z, int(power_str), int(kelvin_limit_str)
        ).send()

    @Binder.binding(Binder.BF_EditFinished, "#electric_heater.power")
    def onPowerEdited(self, params):
        text = params["Text"]
        if text == "":
            return
        if "." in text:
            try:
                val = int(float(text))
                self.power_input.SetText(str(val))
            except ValueError:
                self.power_input.SetText("")
        else:
            try:
                int(text)
            except ValueError:
                self.power_input.SetText("")

    @Binder.binding(Binder.BF_EditFinished, "#electric_heater.kelvin_limit")
    def onKelvinLimitEdited(self, params):
        text = params["Text"]
        if text == "":
            return
        if "." in text:
            try:
                val = int(float(text))
                self.kevin_limit_input.SetText(str(val))
            except ValueError:
                self.kevin_limit_input.SetText("")
        else:
            try:
                if int(text) < 0 or int(text) > 1500:
                    raise ValueError
            except ValueError:
                self.kevin_limit_input.SetText("")
