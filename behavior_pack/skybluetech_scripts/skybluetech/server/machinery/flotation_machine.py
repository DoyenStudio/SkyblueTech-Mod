# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.flotation_machine import (
    FLUID_SLOT_MAX_VOLUMES, STORE_RF_MAX, recipes,
)
from skybluetech_scripts.skybluetech.server.machinery.basic import (
    MultiFluidContainer, Processor,
)
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine


@RegisterMachine
class FlotationMachine(Processor, MultiFluidContainer):
    block_name = Machinery.FLOTATION_MACHINE
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = recipes
    item_input_slots = (0,)
    item_output_slots = (1, 2)
    fluid_input_slots = (0, 1)
    fluid_output_slots = (2,)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    upgrade_slot_start = 3
    upgrade_slots = 4
