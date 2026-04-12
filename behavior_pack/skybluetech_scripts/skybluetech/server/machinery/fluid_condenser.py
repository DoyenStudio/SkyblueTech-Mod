# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import FLUID_CONDENSER as MACHINE_ID
from ...common.machinery_def.fluid_condenser import recipes as Recipes
from ...common.ui_sync.machinery.fluid_condenser import FluidCondenserUISync
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class FluidCondenser(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    process_fluid = True
    process_item = True
    recipes = Recipes
    input_slots = ()
    output_slots = (0,)
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_input_slots = {0}
    fluid_slot_max_volumes = (2000,)
    upgrade_slot_start = 1

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = FluidCondenserUISync.NewServer(self).Activate()

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.fluid_id = self.fluids[0].fluid_id
        self.sync.fluid_volume = self.fluids[0].volume
        self.sync.max_volume = self.fluids[0].max_volume
        self.sync.MarkedAsChanged()
