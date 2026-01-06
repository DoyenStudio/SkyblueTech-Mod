# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen, Binder
from ...define.events.electric_heater import ElectricHeaterSetPowerEvent
from ...ui_sync.machines.electric_heater import ElectricHeaterUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"
DATABAR_TEXT_NODE = MAIN_PATH / "databar/text"
INPUT_NODE = MAIN_PATH / "input"
CONFIRM_BTN_NODE = MAIN_PATH / "confirm_btn"


@RegistProxyScreen("ElectricHeaterUI.main")
class ElectricHeaterUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = ElectricHeaterUISync.NewClient(dim, x, y, z)  # type: ElectricHeaterUISync
        self.sync.WhenUpdated = self.WhenUpdated
        self.power_bar = self.GetElement(POWER_NODE)
        self.databar_text = self.GetElement(DATABAR_TEXT_NODE).asLabel()
        self.input = self.GetElement(INPUT_NODE).asTextEditBox()
        self.confirm_btn = (
            self.GetElement(CONFIRM_BTN_NODE).asButton().SetCallback(self.onSubmitPower)
        )
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        self.databar_text.SetText(
            "设定功率： %d RF/t\n当前温度： %.1f°K"
            % (self.sync.power, self.sync.current_temperature)
        )

    def onSubmitPower(self, _):
        text = self.input.GetText()
        if text == "":
            return
        dim, x, y, z = self.pos
        ElectricHeaterSetPowerEvent(dim, x, y, z, int(text)).send()

    @Binder.binding(Binder.BF_EditFinished, "#electric_heater.input")
    def onTextEdited(self, params):
        text = params["Text"]
        if text == "":
            return
        if "." in text:
            try:
                val = int(float(text))
                self.input.SetText(str(val))
            except ValueError: 
                self.input.SetText("")
        else:
            try:
                int(text)
            except ValueError:
                self.input.SetText("")
