# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import ServerPlaceBlockEntityEvent

from ...common.define.id_enum import Machinery
from ...common.machinery_def.air_compressor import (
    K_PLACED_DIMENSION,
    MAX_FLUID_VOLUME,
    STORE_RF_MAX,
    GetRecipeByDimension,
)
from ...common.machinery_def.air_compressor import (
    recipes as Recipes,
)
from .basic import MultiFluidContainer, Processor
from .core import RegisterMachine


@RegisterMachine
class AirCompressor(Processor, MultiFluidContainer):
    block_name = Machinery.AIR_COMPRESSOR
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_fluid = True
    recipes = Recipes
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_output_slots = (0,)
    fluid_slot_max_volumes = {0: MAX_FLUID_VOLUME}
    item_input_slots = (0, 1, 2, 3)
    item_output_slots = ()
    upgrade_slot_start = 0
    upgrade_slots = 4
    allow_player_use_bucket_push = False

    def __init__(self, dim, x, y, z, block_entity_data):
        super(AirCompressor, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnPlaced(self._air_compressor_on_placed)

    def _air_compressor_on_placed(self, event):
        # type: (ServerPlaceBlockEntityEvent) -> None
        self.bdata[K_PLACED_DIMENSION] = event.dimension
        self.recheck_recipe()
        self.CallSync()

    def get_recipe(self):
        recipe = GetRecipeByDimension(self.placed_dimension)
        if recipe is None:
            return 0, None
        return 0, recipe


    @property
    def placed_dimension(self):
        # type: () -> int
        dimension = self.bdata[K_PLACED_DIMENSION]
        if dimension is None:
            dimension = self.dim
            self.bdata[K_PLACED_DIMENSION] = dimension
        return dimension
