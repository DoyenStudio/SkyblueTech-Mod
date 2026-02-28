# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_STORE_RF = "r"
K_STORE_RF_MAX = "m"
K_POWER = "p"
K_CUR_TEMPERATURE = "t"


class ElectricHeaterUISync(MachineUISync):
    storage_rf = 0
    rf_max = 0
    power = 0
    current_temperature = 0.0

    def Unmarshal(self, data):
        self.storage_rf = data[K_STORE_RF]
        self.rf_max = data[K_STORE_RF_MAX]
        self.power = data[K_POWER]
        self.current_temperature = data[K_CUR_TEMPERATURE]

    def Marshal(self):
        return {
            K_STORE_RF: self.storage_rf,
            K_STORE_RF_MAX: self.rf_max,
            K_POWER: self.power,
            K_CUR_TEMPERATURE: self.current_temperature
        }
