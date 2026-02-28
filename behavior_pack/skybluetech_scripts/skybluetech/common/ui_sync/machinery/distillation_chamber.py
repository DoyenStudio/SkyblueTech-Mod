# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_OUTPUT_RATE = "r"
K_CUR_TEMPERATURE = "t"
K_LOWER_FLUID_ID = "li"
K_LOWER_FLUID_VOLUME = "lv"
K_LOWER_FLUID_MAX_VOLUME = "L"
K_UPPER_FLUID_ID = "ui"
K_UPPER_FLUID_VOLUME = "uv"
K_UPPER_FLUID_MAX_VOLUME = "U"


class DistillationChamberUISync(MachineUISync):
    output_rate = 0.0
    current_temperature = 0.0
    lower_fluid_id = None
    lower_fluid_volume = 0
    lower_fluid_max_volume = 0
    upper_fluid_id = None
    upper_fluid_volume = 0
    upper_fluid_max_volume = 0

    def Unmarshal(self, data):
        self.output_rate = data[K_OUTPUT_RATE]
        self.current_temperature = data[K_CUR_TEMPERATURE]
        self.lower_fluid_id = data[K_LOWER_FLUID_ID]
        self.lower_fluid_volume = data[K_LOWER_FLUID_VOLUME]
        self.lower_fluid_max_volume = data[K_LOWER_FLUID_MAX_VOLUME]
        self.upper_fluid_id = data[K_UPPER_FLUID_ID]
        self.upper_fluid_volume = data[K_UPPER_FLUID_VOLUME]
        self.upper_fluid_max_volume = data[K_UPPER_FLUID_MAX_VOLUME]

    def Marshal(self):
        return {
            K_OUTPUT_RATE: self.output_rate,
            K_CUR_TEMPERATURE: self.current_temperature,
            K_LOWER_FLUID_ID: self.lower_fluid_id,
            K_LOWER_FLUID_VOLUME: self.lower_fluid_volume,
            K_LOWER_FLUID_MAX_VOLUME: self.lower_fluid_max_volume,
            K_UPPER_FLUID_ID: self.upper_fluid_id,
            K_UPPER_FLUID_VOLUME: self.upper_fluid_volume,
            K_UPPER_FLUID_MAX_VOLUME: self.upper_fluid_max_volume
        }
