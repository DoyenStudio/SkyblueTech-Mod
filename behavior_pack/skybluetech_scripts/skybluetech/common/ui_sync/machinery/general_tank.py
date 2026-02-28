# coding=utf-8

from .basic_machine_ui_sync import MachineUISync

K_PUMP_FLUID_ID = "P"
K_PUMP_FLUID_VOLUME = "V"
K_PUMP_MAX_VOLUME = "M"


class GeneralTankUISync(MachineUISync):
    fluid_id = None
    fluid_volume = 0
    max_volume = 0

    def Unmarshal(self, data):
        self.fluid_id = data[K_PUMP_FLUID_ID]
        self.fluid_volume = data[K_PUMP_FLUID_VOLUME]
        self.max_volume = data[K_PUMP_MAX_VOLUME]

    def Marshal(self):
        return {
            K_PUMP_FLUID_ID: self.fluid_id,
            K_PUMP_FLUID_VOLUME: self.fluid_volume,
            K_PUMP_MAX_VOLUME: self.max_volume,
        }
