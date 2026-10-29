# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.fluid_condenser import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from ...common.machinery_def.fluid_condenser import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class FluidCondenser(Processor, MultiFluidContainer):
    block_name = Machinery.FLUID_CONDENSER
    dump_progress_to_block_entity_data = True
    store_rf_max = STORE_RF_MAX
    process_fluid = True
    process_item = True
    recipes = Recipes
    item_input_slots = ()
    item_output_slots = (0,)
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_input_slots = (0,)
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    upgrade_slot_start = 1

    def __init__(self, dim, x, y, z, block_entity_data):
        super(FluidCondenser, self).__init__(dim, x, y, z, block_entity_data)
