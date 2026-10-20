# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent

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
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(fluid_pipe=True)


@RegisterMachine
class GasBurningGenerator(GeneratorProcessor, MultiFluidContainer):
    block_name = Machinery.GAS_BURNING_GENERATOR
    store_rf_max = STORE_RF_MAX
    process_fluid = True
    recipes = Recipes
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_slot_max_volumes = (MAX_INPUT_GAS_VOLUME, MAX_OUTPUT_GAS_VOLUME)

    def __init__(self, dim, x, y, z, block_entity_data):
        super(GasBurningGenerator, self).__init__(dim, x, y, z, block_entity_data)
        self.handler.SubscribeOnPlaced(self._gas_burning_generator_on_placed)
        self.handler.SubscribeOnNeighborChanged(self._gas_burning_generator_on_neighbor_changed)

    def _gas_burning_generator_on_placed(self, _):
        TCON.block_placed(self)

    def _gas_burning_generator_on_neighbor_changed(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)
