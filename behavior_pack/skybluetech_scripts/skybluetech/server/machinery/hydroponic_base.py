# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.hydroponic_base import (
    FLUID_0_MAX_VOLUME,
    FLUID_1_MAX_VOLUME,
)
from .basic import (
    BaseMachine,
    GUIControl,
    ItemContainer,
    MultiFluidContainer,
)
from .core import RegisterMachine

K_GROW_STAGE = "grow_stage"
K_STAGE_GROW_TICKS = "stage_grow_ticks"
WORK_TICK_DELAY = 5
POWER_COST = 4


@RegisterMachine
class HydroponicBase(GUIControl, MultiFluidContainer, ItemContainer):
    block_name = Machinery.HYDROPONIC_BASE
    is_non_energy_machine = True
    input_slots = ()
    output_slots = tuple(range(16))
    fluid_input_slots = {0, 1}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (FLUID_0_MAX_VOLUME, FLUID_1_MAX_VOLUME)
    fluid_io_fix_mode = -1
    running_power = POWER_COST

    def __init__(self, dim, x, y, z, block_entity_data):
        super(HydroponicBase, self).__init__(dim, x, y, z, block_entity_data)


    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        results = (
            MultiFluidContainer.IsValidFluidInput(self, slot, fluid_id),
            self._hydroponic_base_is_valid_fluid_input(slot, fluid_id),
        )
        return all(results)

    def _hydroponic_base_is_valid_fluid_input(self, slot, fluid_id):
        # type: (int, str) -> bool
        if slot == 0:
            return fluid_id == "minecraft:water"
        return False

    def TakeWater(self, volume):
        # type: (float) -> None
        self.fluids[0].volume -= volume
        if self.fluids[0].volume <= 0:
            self.fluids[0].fluid_id = None

    def GetWaterVolume(self):
        # type: () -> float
        return self.fluids[0].volume
