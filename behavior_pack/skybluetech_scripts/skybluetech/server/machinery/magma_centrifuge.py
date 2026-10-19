# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.magma_centrifuge import (
    FLUID_SLOT_MAX_VOLUMES,
    STORE_RF_MAX,
)
from ...common.machinery_def.magma_centrifuge import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class MagmaCentrifuge(Processor, MultiFluidContainer):
    block_name = Machinery.MAGMA_CENTRIFUGE
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_fluid = True
    recipes = Recipes
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_input_slots = {0}
    fluid_output_slots = {1, 2, 3, 4, 5, 6}
    upgrade_slot_start = 0
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        super(MagmaCentrifuge, self).__init__(dim, x, y, z, block_entity_data)
