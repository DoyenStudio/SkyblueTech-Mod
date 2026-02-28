# coding=utf-8

from .basic_machine_ui_sync import MachineUISync, FluidSlotSync

K_FLUIDS = "f"
K_RF = "r"
K_RF_MAX = "m"
K_PROGRESS = "p"


class GeoThermalGeneratorUISync(MachineUISync):
    fluids = [] # type: list[FluidSlotSync]
    storage_rf = 0
    rf_max = 0
    progress = 0.0

    def Unmarshal(self, data):
        FluidSlotSync.UnmarshalList(self.fluids, data[K_FLUIDS])
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.progress = data[K_PROGRESS]

    def Marshal(self):
        return {
            K_FLUIDS: FluidSlotSync.MarshalList(self.fluids),
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_PROGRESS: self.progress
        }
