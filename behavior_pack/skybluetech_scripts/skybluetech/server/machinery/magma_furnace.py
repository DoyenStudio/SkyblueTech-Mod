# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.items import Upgraders
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.MAGMA_FURNACE
from ...common.machinery_def.magma_furnace import (
    magma_factory_recipes as MagmaFactoryRecipes,
    recipes as Recipes,
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
)
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class MagmaFurnace(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
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
    allow_upgrader_tags = Processor.allow_upgrader_tags | {
        "skybluetech:upgraders/spec_magma_factory"
    }

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

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

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass
