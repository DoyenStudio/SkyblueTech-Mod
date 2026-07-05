# coding=utf-8
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.REDSTONE_GENERATOR
from ...common.machinery_def.redstone_generator import recipes as Recipes, STORE_RF_MAX
from .basic import (
    GeneratorProcessor,
    RegisterMachine,
)


@RegisterMachine
class RedstoneGenerator(GeneratorProcessor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
