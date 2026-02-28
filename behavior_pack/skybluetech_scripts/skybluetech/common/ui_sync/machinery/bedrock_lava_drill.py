# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_FLUID_ID = "P"
K_FLUID_VOLUME = "V"
K_MAX_VOLUME = "M"
K_RF = "r"
K_RF_MAX = "m"


class BedrockLavaDrillUISync(MachineUISync):
    fluid_id = None
    fluid_volume = 0
    max_volume = 0
    storage_rf = 0
    rf_max = 0

    def Unmarshal(self, data):
        self.fluid_id = data[K_FLUID_ID]
        self.fluid_volume = data[K_FLUID_VOLUME]
        self.max_volume = data[K_MAX_VOLUME]
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]

    def Marshal(self):
        return {
            K_FLUID_ID: self.fluid_id,
            K_FLUID_VOLUME: self.fluid_volume,
            K_MAX_VOLUME: self.max_volume,
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
        }
