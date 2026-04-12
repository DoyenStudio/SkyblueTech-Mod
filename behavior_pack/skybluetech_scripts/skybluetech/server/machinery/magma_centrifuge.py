# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import MAGMA_CENTRIFUGE as MACHINE_ID
from ...common.machinery_def.magma_centrifuge import recipes as Recipes
from ...common.ui_sync.machinery.magma_centrifuge import (
    MagmaCentrifugeUISync,
    FluidSlotSync,
)
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class MagmaCentrifuge(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    process_fluid = True
    recipes = Recipes
    fluid_slot_max_volumes = (8000, 1000, 1000, 1000, 1000, 1000, 1000)
    fluid_input_slots = {0}
    fluid_output_slots = {1, 2, 3, 4, 5, 6}
    upgrade_slot_start = 0
    upgrade_slots = 4

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = MagmaCentrifugeUISync.NewServer(self).Activate()

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
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()
