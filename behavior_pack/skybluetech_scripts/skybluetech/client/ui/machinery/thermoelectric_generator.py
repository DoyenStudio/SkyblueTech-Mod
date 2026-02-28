# coding=utf-8

from skybluetech_scripts.tooldelta.ui.reg import RegistToolDeltaScreen
from skybluetech_scripts.tooldelta.ui.utils import UIPath
from ....common.ui_sync.machinery.thermoelectric_generator import (
    ThermoelectricGeneratorUISync,
)
from .utils import UpdatePowerBar, FormatRF
from .define import MachinePanelUI


TOP_NODE = UIPath("/ThermoelectricGenerator")
CENTER_NODE = TOP_NODE / "center"
heat_disp_node = CENTER_NODE / "heat_disp"
cool_disp_node = CENTER_NODE / "cool_disp"
power_disp_node = CENTER_NODE / "power_disp"
power_bar_node = TOP_NODE / "PowerBar"


@RegistToolDeltaScreen("ThermoelectricGeneratorUI.main")
class ThermoelectricGeneratorUI(MachinePanelUI):
    def __init__(self, namespace, name, param):
        MachinePanelUI.__init__(self, namespace, name, param)
        self.sync = ThermoelectricGeneratorUISync.NewClient(param["sync"])  # type: ThermoelectricGeneratorUISync
        self.sync.WhenUpdated = self.WhenUpdated

    def Create(self):
        self.heat_label = self[heat_disp_node].asLabel()
        self.cool_label = self[cool_disp_node].asLabel()
        self.power_label = self[power_disp_node].asLabel()
        self.power_bar = self[power_bar_node]

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        self.heat_label.SetText(str(self.sync.heat_val))
        self.cool_label.SetText(str(self.sync.cool_val))
        self.power_label.SetText("%s/t" % FormatRF(self.sync.power))
