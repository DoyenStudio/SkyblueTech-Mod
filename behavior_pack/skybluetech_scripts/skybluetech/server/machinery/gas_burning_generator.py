# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum import Machinery
MACHINE_ID = Machinery.GAS_BURNING_GENERATOR
from ...common.machinery_def.gas_burning_generator import (
    recipes as Recipes,
    MAX_INPUT_GAS_VOLUME,
    MAX_OUTPUT_GAS_VOLUME,
    STORE_RF_MAX,
)
from .basic import (
    GeneratorProcessor,
    MultiFluidContainer,
    RegisterMachine,
)
from .utils.transmitter_conn import TransmitterConn

TCON = TransmitterConn(pipe=True)


@RegisterMachine
class GasBurningGenerator(MultiFluidContainer, GeneratorProcessor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    process_fluid = True
    recipes = Recipes
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_slot_max_volumes = (MAX_INPUT_GAS_VOLUME, MAX_OUTPUT_GAS_VOLUME)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        pass

    @SuperExecutorMeta.execute_super
    def OnPlaced(self, _):
        TCON.block_placed(self)

    def OnNeighborChanged(self, event):
        # type: (BlockNeighborChangedServerEvent) -> None
        TCON.neighbor_block_changed(self, event)

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass
