# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistToolDeltaScreen
from ...ui_sync.machinery.wind_generator import WindGeneratorUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar

POWER_NODE = MAIN_PATH / "power_bar"
TEXT_NODE = MAIN_PATH / "text"


@RegistToolDeltaScreen("WindGeneratorUI.main", is_proxy=True)
class WindGeneratorUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = WindGeneratorUISync.NewClient(dim, x, y, z) # type: WindGeneratorUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.text = self.GetElement(TEXT_NODE).asLabel()
        self.sync.WhenUpdated = self.WhenUpdated

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        self.text.SetText("风强度: %d MCW\n输出功率: %d RF/t" % (self.sync.mcw, self.sync.power))

