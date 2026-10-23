# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.oil_extractor import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from ...common.machinery_def.oil_extractor import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class OilExtractor(Processor, MultiFluidContainer):
    block_name = Machinery.OIL_EXTRACTOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    item_input_slots = (0,)
    item_output_slots = ()
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_output_slots = (0,)
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    upgrade_slot_start = 1

    def __init__(self, dim, x, y, z, block_entity_data):
        super(OilExtractor, self).__init__(dim, x, y, z, block_entity_data)
