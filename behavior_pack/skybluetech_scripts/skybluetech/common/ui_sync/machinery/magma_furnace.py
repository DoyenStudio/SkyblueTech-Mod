# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_PROGRESS = "p"
K_RF = "r"
K_RF_MAX = "m"
K_FLUID_ID = "f"
K_FLUID_VOLUME = "v"
K_MAX_FLUID_VOLUME = "M"


class MagmaFurnaceUISync(MachineUISync):
    progress_relative = 0.0
    storage_rf = 0
    rf_max = 0
    fluid_id = None # type: str | None
    fluid_volume = 0.0
    max_volume = 0.0

    def Unmarshal(self, data):
        self.progress_relative = data[K_PROGRESS]
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.fluid_id = data[K_FLUID_ID]
        self.fluid_volume = data[K_FLUID_VOLUME]
        self.max_volume = data[K_MAX_FLUID_VOLUME]

    def Marshal(self):
        return {
            K_PROGRESS: self.progress_relative,
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_FLUID_ID: self.fluid_id,
            K_FLUID_VOLUME: self.fluid_volume,
            K_MAX_FLUID_VOLUME: self.max_volume
        }
