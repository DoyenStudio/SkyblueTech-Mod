# coding=utf-8
#
from .basic_machine_ui_sync import MachineUISync

K_LIGHT_LEVEL = "l"
K_RF = "r"
K_RF_MAX = "m"
K_POWER_OUTPUT = "p"


class SolarPanelUISync(MachineUISync):
    light_level = 0
    storage_rf = 0
    rf_max = 0
    power = 0

    def Unmarshal(self, data):
        self.light_level = data[K_LIGHT_LEVEL]
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.power = data[K_POWER_OUTPUT]

    def Marshal(self):
        return {
            K_LIGHT_LEVEL: self.light_level,
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_POWER_OUTPUT: self.power
        }


