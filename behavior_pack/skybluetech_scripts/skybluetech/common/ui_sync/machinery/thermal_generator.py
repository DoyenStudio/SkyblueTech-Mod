# coding=utf-8
#
from .basic_machine_ui_sync import MachineUISync

K_BURNTIME_RELATIVE = "b"
K_RF = "r"
K_RF_MAX = "m"
K_POWER_OUTPUT = "p"


class ThermalGeneratorUISync(MachineUISync):
    rest_burn_relative = 0.0
    storage_rf = 0
    rf_max = 0
    power = 0

    def Unmarshal(self, data):
        self.rest_burn_relative = data[K_BURNTIME_RELATIVE]
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.power = data[K_POWER_OUTPUT]

    def Marshal(self):
        return {
            K_BURNTIME_RELATIVE: self.rest_burn_relative,
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_POWER_OUTPUT: self.power
        }


