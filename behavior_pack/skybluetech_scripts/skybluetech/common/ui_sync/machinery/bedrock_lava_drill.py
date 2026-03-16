# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"
K_LAVA_REST_PERCENT = "l"


class BedrockLavaDrillUISync(MachineUISync):
    storage_rf = 0
    rf_max = 0
    lava_rest_percent = 0.0

    def Unmarshal(self, data):
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.lava_rest_percent = data[K_LAVA_REST_PERCENT]

    def Marshal(self):
        return {
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_LAVA_REST_PERCENT: self.lava_rest_percent,
        }
