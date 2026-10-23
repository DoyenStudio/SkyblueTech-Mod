# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.engraver import (
    FLUID_SLOT_MAX_VOLUMES,
    STORE_RF_MAX,
)
from ...common.machinery_def.engraver import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class Engraver(Processor, MultiFluidContainer):
    """蚀刻机: 4 物品输入槽 + 1 物品输出槽 + 4 升级槽, 2 个流体槽均为输入。"""

    block_name = Machinery.ENGRAVER
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    item_input_slots = (0, 1, 2, 3)
    item_output_slots = (4,)
    upgrade_slot_start = 5
    upgrade_slots = 4
    fluid_input_slots = (0, 1)
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES

    def __init__(self, dim, x, y, z, block_entity_data):
        super(Engraver, self).__init__(dim, x, y, z, block_entity_data)
