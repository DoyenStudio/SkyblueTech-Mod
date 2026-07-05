# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.MAGMA_CENTRIFUGE
from ...common.machinery_def.magma_centrifuge import (
    recipes as Recipes,
    STORE_RF_MAX,
    FLUID_SLOT_MAX_VOLUMES,
)
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class MagmaCentrifuge(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_fluid = True
    recipes = Recipes
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_input_slots = {0}
    fluid_output_slots = {1, 2, 3, 4, 5, 6}
    upgrade_slot_start = 0
    upgrade_slots = 4

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass
