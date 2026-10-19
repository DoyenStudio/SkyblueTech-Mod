# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.mixer import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from ...common.machinery_def.mixer import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class Mixer(Processor, MultiFluidContainer):
    block_name = Machinery.MIXER
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    fluid_input_slots = {0}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (MAX_FLUID_VOLUME,)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Mixer, self).__init__(dim, x, y, z, block_entity_data)
