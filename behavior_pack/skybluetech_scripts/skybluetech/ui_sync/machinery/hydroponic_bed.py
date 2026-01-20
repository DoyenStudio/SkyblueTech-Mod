# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"
K_CROP_ID = "i"
K_GROW_STAGE = "s"


class HydroponicBedUISync(MachineUISync):
    store_rf = 0
    rf_max = 1
    crop_id = ""
    grow_stage = 0

    def Unmarshal(self, data):
        self.store_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.crop_id = data[K_CROP_ID]
        self.grow_stage = data[K_GROW_STAGE]

    def Marshal(self):
        return {
            K_RF: self.store_rf,
            K_RF_MAX: self.rf_max,
            K_CROP_ID: self.crop_id,
            K_GROW_STAGE: self.grow_stage,
        }
