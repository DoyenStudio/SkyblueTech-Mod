# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import HYDROPONIC_BASE as MACHINE_ID
from ...common.ui_sync.machinery.hydroponic_base import HydroponicBaseUISync
from .basic import (
    BaseMachine,
    ItemContainer,
    MultiFluidContainer,
    GUIControl,
    RegisterMachine,
)

K_GROW_STAGE = "grow_stage"
K_STAGE_GROW_TICKS = "stage_grow_ticks"
WORK_TICK_DELAY = 5
POWER_COST = 4


@RegisterMachine
class HydroponicBase(BaseMachine, ItemContainer, MultiFluidContainer, GUIControl):
    block_name = MACHINE_ID
    is_non_energy_machine = True
    input_slots = ()
    output_slots = tuple(range(16))
    fluid_input_slots = {0, 1}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (2000, 2000)
    fluid_io_fix_mode = -1
    running_power = POWER_COST

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = HydroponicBaseUISync.NewServer(self).Activate()
        self.CallSync()

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    def OnSync(self):
        self.sync.fluid_1_type = self.fluids[0].fluid_id
        self.sync.fluid_1_volume = self.fluids[0].volume
        self.sync.fluid_1_max_volume = self.fluids[0].max_volume
        self.sync.fluid_2_type = self.fluids[1].fluid_id
        self.sync.fluid_2_volume = self.fluids[1].volume
        self.sync.fluid_2_max_volume = self.fluids[1].max_volume
        self.sync.MarkedAsChanged()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        if slot == 0:
            return fluid_id == "minecraft:water"
        return False

    def TakeWater(self, volume):
        # type: (float) -> None
        self.fluids[0].volume -= volume
        if self.fluids[0].volume <= 0:
            self.fluids[0].fluid_id = None
        self.OnSync()

    def GetWaterVolume(self):
        # type: () -> float
        return self.fluids[0].volume
