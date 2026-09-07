# coding=utf-8
from ...common.define.id_enum import Machinery
from ...common.machinery_def.mixed_macerator import STORE_RF_MAX
from ...common.machinery_def.mixed_macerator import recipes as Recipes
from .basic import Processor, RegisterMachine


@RegisterMachine
class MixedMacerator(Processor):
    block_name = Machinery.MIXED_MACERATOR
    dump_progress_to_block_entity_data = True
    store_rf_max = STORE_RF_MAX
    process_item = True
    recipes = Recipes
    input_slots = (0, 1, 2)
    output_slots = (3,)
    upgrade_slot_start = 4
    upgrade_slots = 4
