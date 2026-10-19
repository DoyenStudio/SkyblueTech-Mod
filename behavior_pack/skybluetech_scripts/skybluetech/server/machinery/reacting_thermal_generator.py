# coding=utf-8

from ...common.define.id_enum import Machinery
from ...common.machinery_def.reacting_thermal_generator import (
    MAX_FLUID_VOLUMES,
    STORE_RF_MAX,
)
from ...common.machinery_def.reacting_thermal_generator import (
    recipes as Recipes,
)
from .basic import (
    GeneratorProcessor,
    MultiFluidContainer,
)
from .core import RegisterMachine


@RegisterMachine
class ReactingThermalGenerator(GeneratorProcessor, MultiFluidContainer):
    block_name = Machinery.REACTING_THERMAL_GENERATOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    input_slots = (0,)
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_slot_max_volumes = MAX_FLUID_VOLUMES

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ReactingThermalGenerator, self).__init__(dim, x, y, z, block_entity_data)
