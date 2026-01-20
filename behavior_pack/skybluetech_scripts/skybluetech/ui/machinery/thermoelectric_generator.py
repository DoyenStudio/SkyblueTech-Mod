# coding=utf-8

from skybluetech_scripts.tooldelta.ui.reg import RegistScreen
from skybluetech_scripts.tooldelta.ui.utils import UIPath
from ...utils.fmt import FormatRF
from ...ui_sync.machinery.thermoelectric_generator import ThermoelectricGeneratorUISync
from .utils import UpdatePowerBar
from .define import MachinePanelUI, MAIN_PATH


TOP_NODE = UIPath("/ThermoelectricGenerator")
CENTER_NODE = TOP_NODE / "center"
heat_disp_node = CENTER_NODE / "heat_disp"
cool_disp_node = CENTER_NODE / "cool_disp"
power_disp_node = CENTER_NODE / "power_disp"
power_bar_node = TOP_NODE / "PowerBar"


@RegistScreen("ThermoelectricGeneratorUI.main")
class ThermoelectricGeneratorUI(MachinePanelUI):

    def __init__(self, namespace, name, param):
        MachinePanelUI.__init__(self, namespace, name, param)
        self.sync = ThermoelectricGeneratorUISync.NewClient(param["sync"]) # type: ThermoelectricGeneratorUISync
        self.sync.WhenUpdated = self.WhenUpdated

    def Create(self):
        MachinePanelUI.Create(self)
        self.heat_label = self[heat_disp_node].asLabel()
        self.cool_label = self[cool_disp_node].asLabel()
        self.power_label = self[power_disp_node].asLabel()
        self.power_bar = self > power_bar_node

    def WhenUpdated(self):
        if not self.inited:
            return
        UpdatePowerBar(self.power_bar, self.sync.storage_rf, self.sync.rf_max)
        self.heat_label.SetText(str(self.sync.heat_val))
        self.cool_label.SetText(str(self.sync.cool_val))
        self.power_label.SetText("%s/t" % FormatRF(self.sync.power))
