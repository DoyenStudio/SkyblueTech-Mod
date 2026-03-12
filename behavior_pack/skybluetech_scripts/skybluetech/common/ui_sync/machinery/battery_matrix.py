# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_RF = "r"
K_RF_MAX = "m"
K_ENABLE_INPUT = "i"
K_ENABLE_OUTPUT = "o"
K_STRUCTURE_FLAG = "f"
K_STRUCTURE_LACKED_BLOCKS = "l"
K_INPUT_POWER = "ip"
K_OUTPUT_POWER = "op"


class BatteryMatrixUISync(MachineUISync):
    storage_rf = 0
    rf_max = 0
    enable_input = False
    enable_output = False
    input_power = 0
    output_power = 0
    structure_flag = 0
    structure_lacked_blocks = {}  # type: dict[str, int]

    def Unmarshal(self, data):
        self.storage_rf = data[K_RF]
        self.rf_max = data[K_RF_MAX]
        self.enable_input = data[K_ENABLE_INPUT]
        self.enable_output = data[K_ENABLE_OUTPUT]
        self.input_power = data[K_INPUT_POWER]
        self.output_power = data[K_OUTPUT_POWER]
        self.structure_flag = data[K_STRUCTURE_FLAG]
        self.structure_lacked_blocks = data[K_STRUCTURE_LACKED_BLOCKS]

    def Marshal(self):
        return {
            K_RF: self.storage_rf,
            K_RF_MAX: self.rf_max,
            K_ENABLE_INPUT: self.enable_input,
            K_ENABLE_OUTPUT: self.enable_output,
            K_INPUT_POWER: self.input_power,
            K_OUTPUT_POWER: self.output_power,
            K_STRUCTURE_FLAG: self.structure_flag,
            K_STRUCTURE_LACKED_BLOCKS: self.structure_lacked_blocks,
        }
