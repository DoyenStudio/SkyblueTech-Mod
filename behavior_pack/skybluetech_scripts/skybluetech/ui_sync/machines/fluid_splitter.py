# coding=utf-8

from .basic_machine_ui_sync import MachineUISync, FluidSlotSync

K_FLUIDS = "f"


class FluidSplitterUISync(MachineUISync):
    fluids = [] # type: list[FluidSlotSync]

    def Unmarshal(self, data):
        FluidSlotSync.UnmarshalList(self.fluids, data[K_FLUIDS])

    def Marshal(self):
        return {
            K_FLUIDS: FluidSlotSync.MarshalList(self.fluids)
        }
