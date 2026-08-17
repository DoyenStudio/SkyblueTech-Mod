# coding=utf-8
from ...common.define.id_enum.machinery import Machinery
from ...common.machinery_def.sawmill import recipes as Recipes, STORE_RF_MAX
from .basic import RegisterMachine, Processor


@RegisterMachine
class Sawmill(Processor):
    """锯木机: 1 输入 / 3 输出 + 4 升级槽。"""

    block_name = Machinery.SAWMILL
    dump_progress_to_block_entity_data = True
    store_rf_max = STORE_RF_MAX
    process_item = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1, 2, 3)
    upgrade_slot_start = 4
    upgrade_slots = 4
