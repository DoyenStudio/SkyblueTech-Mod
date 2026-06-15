# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import ServerPlaceBlockEntityEvent
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import AIR_COMPRESSOR as MACHINE_ID
from ...common.machinery_def.air_compressor import (
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
    K_PLACED_DIMENSION,
    GetRecipeByDimension,
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class AirCompressor(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_fluid = True
    recipes = Recipes
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_output_slots = {0}
    fluid_slot_max_volumes = (MAX_FLUID_VOLUME,)
    input_slots = (0, 1, 2, 3)
    output_slots = ()
    upgrade_slot_start = 0
    upgrade_slots = 4
    allow_player_use_bucket_push = False

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, event):
        # type: (ServerPlaceBlockEntityEvent) -> None
        self.bdata[K_PLACED_DIMENSION] = event.dimension
        self.recheck_recipe()
        self.CallSync()

    def get_recipe(self):
        recipe = GetRecipeByDimension(self.placed_dimension)
        if recipe is None:
            return 0, None
        return 0, recipe

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass

    @property
    def placed_dimension(self):
        # type: () -> int
        dimension = self.bdata[K_PLACED_DIMENSION]
        if dimension is None:
            dimension = self.dim
            self.bdata[K_PLACED_DIMENSION] = dimension
        return dimension
