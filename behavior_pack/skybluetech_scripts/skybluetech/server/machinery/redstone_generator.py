# coding=utf-8
from ...common.define.id_enum import Machinery
from ...common.define.id_enum.items import Upgraders
from ...common.machinery_def.redstone_generator import STORE_RF_MAX
from ...common.machinery_def.redstone_generator import recipes as Recipes
from .basic import (
    GeneratorProcessor,
)
from .core import RegisterMachine


@RegisterMachine
class RedstoneGenerator(GeneratorProcessor):
    block_name = Machinery.REDSTONE_GENERATOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = Recipes
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 1
    allow_upgraders = frozenset({Upgraders.GENERIC_AUTO_EJECTION})
