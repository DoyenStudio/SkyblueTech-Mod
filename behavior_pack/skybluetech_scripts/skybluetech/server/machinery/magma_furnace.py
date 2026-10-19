# coding=utf-8

from ...common.define.id_enum import Machinery, Upgraders
from ...common.machinery_def.magma_furnace import (
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
)
from ...common.machinery_def.magma_furnace import (
    magma_factory_recipes as MagmaFactoryRecipes,
)
from ...common.machinery_def.magma_furnace import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class MagmaFurnace(Processor, MultiFluidContainer):
    block_name = Machinery.MAGMA_FURNACE
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = Recipes
    origin_process_ticks = 20 * 8  # 8s
    input_slots = (0,)
    output_slots = (1,)
    fluid_slot_max_volumes = (MAX_FLUID_VOLUME,)
    fluid_output_slots = {0}
    upgrade_slot_start = 1
    upgrade_slots = 4
    allow_upgraders = Processor.allow_upgraders | frozenset({
        Upgraders.SPEC_MAGMA_FACTORY,
    })

    def __init__(self, dim, x, y, z, block_entity_data):
        super(MagmaFurnace, self).__init__(dim, x, y, z, block_entity_data)

    def UpdateUpgraders(self, upgraders):
        # type: (dict[str, int]) -> None
        Processor.UpdateUpgraders(self, upgraders)
        self.recipes = (
            MagmaFactoryRecipes
            if self.HasUpgrader(Upgraders.SPEC_MAGMA_FACTORY)
            else Recipes
        )
        if hasattr(self, "current_recipe"):
            self.recheck_recipe()
