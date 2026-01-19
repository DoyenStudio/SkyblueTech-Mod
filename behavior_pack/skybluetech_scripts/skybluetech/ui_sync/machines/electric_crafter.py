# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"
K_PROGRESS = "p"


class ElectricCrafterUISync(MachineUISync):
    rf = 0
    rf_max = 0
    progress = 0.0

    def Unmarshal(self, data):
        self.rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.progress = data[K_PROGRESS]

    def Marshal(self):
        return {
            K_RF: self.rf,
            K_RF_MAX: self.rf_max,
            K_PROGRESS: self.progress
        }
