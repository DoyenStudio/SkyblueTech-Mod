# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"
K_FLUID_ID = "F"
K_FLUID_VOLUME = "V"
K_MAX_VOLUME = "M"
K_DRILL_PROGRESS = "d"
K_LAVA_STORAGE_LEFT = "l"
K_STRUCTURE_FLAG = "s"
K_STRUCTURE_LACKED_BLOCKS = "b"


class BedrockLavaDrillUISync(MachineUISync):
    storage_rf = 0
    rf_max = 0
    work_mode = 0
    fluid_id = None  # type: str | None
    fluid_volume = 0.0
    max_volume = 1.0
    drill_progress = 0.0
    lava_storage_left = 0.0
    structure_flag = 0
    structure_lacked_blocks = {}  # type: dict[str, int]

    def Unmarshal(self, data):
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.fluid_id = data[K_FLUID_ID]
        self.fluid_volume = data[K_FLUID_VOLUME]
        self.max_volume = data[K_MAX_VOLUME]
        self.drill_progress = data[K_DRILL_PROGRESS]
        self.lava_storage_left = data[K_LAVA_STORAGE_LEFT]
        self.structure_flag = data[K_STRUCTURE_FLAG]
        self.structure_lacked_blocks = data[K_STRUCTURE_LACKED_BLOCKS]

    def Marshal(self):
        return {
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_FLUID_ID: self.fluid_id,
            K_FLUID_VOLUME: self.fluid_volume,
            K_MAX_VOLUME: self.max_volume,
            K_DRILL_PROGRESS: self.drill_progress,
            K_LAVA_STORAGE_LEFT: self.lava_storage_left,
            K_STRUCTURE_FLAG: self.structure_flag,
            K_STRUCTURE_LACKED_BLOCKS: self.structure_lacked_blocks,
        }
