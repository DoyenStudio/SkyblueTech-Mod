# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

from ...common.define.id_enum import Machinery
from ...common.machinery_def.gas_burning_generator import (
    MAX_INPUT_GAS_VOLUME,
    MAX_OUTPUT_GAS_VOLUME,
    STORE_RF_MAX,
)
from ...common.machinery_def.gas_burning_generator import (
    recipes as Recipes,
)
from .basic import (
    GeneratorProcessor,
    MultiFluidContainer,
)
from .core import RegisterMachine
from .basic.slot_reads import SlotReads, accepts_slot_reads
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(fluid_pipe=True)


@RegisterMachine
class GasBurningGenerator(GeneratorProcessor, MultiFluidContainer):
    block_name = Machinery.GAS_BURNING_GENERATOR
    store_rf_max = STORE_RF_MAX
    process_fluid = True
    recipes = Recipes
    fluid_input_slots = (0, 2)
    fluid_output_slots = (1,)
    fluid_slot_max_volumes = {
        0: MAX_INPUT_GAS_VOLUME,
        1: MAX_OUTPUT_GAS_VOLUME,
        2: MAX_INPUT_GAS_VOLUME,
    }
    # Chlorine uses the separate top inlet; fuel gases use slot 0.
    fluid_input_slots_by_face = {
        RelativeFacingStrEnum.TOP: (2,),
        RelativeFacingStrEnum.FRONT: (0,),
        RelativeFacingStrEnum.BACK: (0,),
        RelativeFacingStrEnum.LEFT: (0,),
        RelativeFacingStrEnum.RIGHT: (0,),
        RelativeFacingStrEnum.DOWN: (0,),
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        super(GasBurningGenerator, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnPlaced(self._gas_burning_generator_on_placed)
        self.handler.SubscribeOnNeighborChanged(self._gas_burning_generator_on_neighbor_changed)

    def _gas_burning_generator_on_placed(self, _):
        TCON.block_placed(self)

    @accepts_slot_reads
    def get_recipe(self, slot_reads=None):
        reads = slot_reads or SlotReads(self)
        if self.recipe_index is None:
            # Prefer the two-gas reaction without changing saved recipe indices.
            for recipe_index, recipe in enumerate(self.recipes):
                if recipe.second_gas_id is None:
                    continue
                if reads.allocate_fluid_inputs(recipe) is not None:
                    return recipe_index, recipe
        return GeneratorProcessor.get_recipe(self, reads)

    def _gas_burning_generator_on_neighbor_changed(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)
