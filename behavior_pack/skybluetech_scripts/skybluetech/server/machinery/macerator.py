# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.MACERATOR
from ...common.machinery_def.macerator import recipes as Recipes, STORE_RF_MAX
from .basic import RegisterMachine, Processor


@RegisterMachine
class Macerator(Processor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4
