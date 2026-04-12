# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import BlockNeighborChangedServerEvent
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum import GAS_BURNING_GENERATOR as MACHINE_ID
from ...common.machinery_def.gas_burning_generator import recipes as Recipes
from ...common.ui_sync.machinery.gas_burning_generator import (
    GasBurningGeneratorUISync,
    FluidSlotSync,
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
    store_rf_max = 28800
    process_fluid = True
    recipes = Recipes
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = (2000, 2000)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = GasBurningGeneratorUISync.NewServer(self).Activate()
        self.CallSync()

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

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress = float(self.fluids[0].volume) / self.fluids[0].max_volume
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()
