# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_STORE_RF = "r"
K_STORE_RF_MAX = "m"


class FluidInterfaceUISync(MachineUISync):
    storage_rf = 0
    rf_max = 0

    def Unmarshal(self, data):
        self.storage_rf = data[K_STORE_RF]
        self.rf_max = data[K_STORE_RF_MAX]

    def Marshal(self):
        return {
            K_STORE_RF: self.storage_rf,
            K_STORE_RF_MAX: self.rf_max
        }
