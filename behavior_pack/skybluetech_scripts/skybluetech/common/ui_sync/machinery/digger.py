# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_PROGRESS = "p"
K_RF = "r"
K_RF_MAX = "m"
K_BLOCKID = "b"
K_BLOCKAUX = "a"


class DiggerUISync(MachineUISync):
    progress_relative = 0.0
    storage_rf = 0
    rf_max = 0
    block_id = "minecraft:barrier"
    block_aux = 0

    def Unmarshal(self, data):
        self.progress_relative = data[K_PROGRESS]
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.block_id = data[K_BLOCKID]
        self.block_aux = data[K_BLOCKAUX]

    def Marshal(self):
        return {
            K_PROGRESS: self.progress_relative,
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_BLOCKID: self.block_id,
            K_BLOCKAUX: self.block_aux,
        }
