# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.macerator import STORE_RF_MAX
from ...common.machinery_def.macerator import recipes as Recipes
from .basic import Processor
from .core import RegisterMachine


@RegisterMachine
class Macerator(Processor):
    block_name = Machinery.MACERATOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = Recipes
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4
