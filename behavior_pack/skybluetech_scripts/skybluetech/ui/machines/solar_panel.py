# coding=utf-8

from skybluetech_scripts.tooldelta.ui import RegistProxyScreen
from ...ui_sync.machines.solar_panel import SolarPanelUISync
from .define import MachinePanelUIProxy, MAIN_PATH
from .utils import UpdatePowerBar, UpdateGenericProgressT2B

POWER_NODE = MAIN_PATH / "power_bar"
SUN_NODE = MAIN_PATH / "progress"
TEXT_NODE = MAIN_PATH / "text"


@RegistProxyScreen("SolarPanelUI.main")
class SolarPanelUI(MachinePanelUIProxy):
    def OnCreate(self):
        dim, x, y, z = self.pos
        self.sync = SolarPanelUISync.NewClient(dim, x, y, z) # type: SolarPanelUISync
        self.power_bar = self.GetElement(POWER_NODE)
        self.sun = self.GetElement(SUN_NODE)
        self.text = self.GetElement(TEXT_NODE).asLabel()
        self.sync.WhenUpdated = self.WhenUpdated
        MachinePanelUIProxy.OnCreate(self)

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        UpdateGenericProgressT2B(self.sun, float(self.sync.light_level) / 15)
        self.text.SetText("太阳光强度: %d MCLux\n电池板输出功率: %d RF/t" % (self.sync.light_level, self.sync.power))

