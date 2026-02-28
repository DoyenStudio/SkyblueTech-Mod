# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_FLUID_1_TYPE = "t1"
K_FLUID_1_VOLUME = "v1"
K_FLUID_1_MAX_VOLUME = "M1"
K_FLUID_2_TYPE = "t2"
K_FLUID_2_VOLUME = "v2"
K_FLUID_2_MAX_VOLUME = "M2"


class HydroponicBaseUISync(MachineUISync):
    fluid_1_type = None # type: str | None
    fluid_1_volume = 0.0 # type: float
    fluid_1_max_volume = 0.0 # type: float
    fluid_2_type = None # type: str | None
    fluid_2_volume = 0.0 # type: float
    fluid_2_max_volume = 0.0 # type: float

    def Unmarshal(self, data):
        self.fluid_1_type = data[K_FLUID_1_TYPE]
        self.fluid_1_volume = data[K_FLUID_1_VOLUME]
        self.fluid_1_max_volume = data[K_FLUID_1_MAX_VOLUME]
        self.fluid_2_type = data[K_FLUID_2_TYPE]
        self.fluid_2_volume = data[K_FLUID_2_VOLUME]
        self.fluid_2_max_volume = data[K_FLUID_2_MAX_VOLUME]

    def Marshal(self):
        return {
            K_FLUID_1_TYPE: self.fluid_1_type,
            K_FLUID_1_VOLUME: self.fluid_1_volume,
            K_FLUID_1_MAX_VOLUME: self.fluid_1_max_volume,
            K_FLUID_2_TYPE: self.fluid_2_type,
            K_FLUID_2_VOLUME: self.fluid_2_volume,
            K_FLUID_2_MAX_VOLUME: self.fluid_2_max_volume
        }
