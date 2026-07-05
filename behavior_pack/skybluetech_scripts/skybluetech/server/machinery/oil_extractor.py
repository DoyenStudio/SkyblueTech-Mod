# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.OIL_EXTRACTOR
from ...common.machinery_def.oil_extractor import (
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class OilExtractor(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = ()
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_output_slots = {0}
    fluid_slot_max_volumes = (MAX_FLUID_VOLUME,)
    upgrade_slot_start = 1

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass
