# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.metal_press import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from ...common.machinery_def.metal_press import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class MetalPress(Processor, MultiFluidContainer):
    block_name = Machinery.METAL_PRESS
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    item_input_slots = (0,)
    item_output_slots = (1,)
    fluid_input_slots = (0,)
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}

    def __init__(self, dim, x, y, z, block_entity_data):
        super(MetalPress, self).__init__(dim, x, y, z, block_entity_data)
