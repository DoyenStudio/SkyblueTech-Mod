# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"


class BatteryCubeUISync(MachineUISync):
    progress_relative = 0.0
    storage_rf = 0
    rf_max = 0

    def Unmarshal(self, data):
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]

    def Marshal(self):
        return {
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
        }


