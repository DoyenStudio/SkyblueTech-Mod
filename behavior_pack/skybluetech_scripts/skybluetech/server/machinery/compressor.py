# coding=utf-8
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.COMPRESSOR
from ...common.machinery_def.compressor import recipes as Recipes, STORE_RF_MAX
from .basic import RegisterMachine, Processor


@RegisterMachine
class Compressor(Processor):
    block_name = MACHINE_ID
    dump_progress_to_block_entity_data = True
    store_rf_max = STORE_RF_MAX
    process_item = True
    recipes = Recipes
    input_slots = (0, 1, 2)
    output_slots = (3,)
    upgrade_slot_start = 4
    upgrade_slots = 4
