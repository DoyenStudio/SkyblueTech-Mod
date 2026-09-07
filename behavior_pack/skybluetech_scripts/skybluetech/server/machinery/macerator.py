# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta

from ...common.define.id_enum import Machinery
from ...common.machinery_def.macerator import STORE_RF_MAX
from ...common.machinery_def.macerator import recipes as Recipes
from .basic import Processor, RegisterMachine


@RegisterMachine
class Macerator(Processor):
    block_name = Machinery.MACERATOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4
