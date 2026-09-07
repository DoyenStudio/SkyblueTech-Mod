# coding=utf-8
from ...common.define.id_enum import Machinery
from ...common.machinery_def.alloy_furnace import RF_MAX
from ...common.machinery_def.alloy_furnace import recipes as Recipes
from .basic import Processor, RegisterMachine


@RegisterMachine
class AlloyFurnace(Processor):
    block_name = Machinery.ALLOY_FURNACE
    store_rf_max = RF_MAX
    process_item = True
    recipes = Recipes
    input_slots = (0, 1, 2, 3)
    output_slots = (4, 5)
    upgrade_slot_start = 6
