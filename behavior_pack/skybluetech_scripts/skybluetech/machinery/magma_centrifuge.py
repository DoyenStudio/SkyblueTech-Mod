# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..define.id_enum.machinery import MAGMA_CENTRIFUGE as MACHINE_ID
from ..machinery_def.magma_centrifuge import recipes as Recipes
from ..ui_sync.machines.magma_centrifuge import MagmaCentrifugeUISync, FluidSlotSync
from .basic import MixedProcessor, RegisterMachine


@RegisterMachine
class MagmaCentrifuge(MixedProcessor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    fluid_slot_max_volumes = (8000, 1000, 1000, 1000, 1000, 1000, 1000)
    fluid_io_mode = (1, 0, 1, 1, 1, 1)
    recipes = Recipes
    fluid_input_slots = {0}
    fluid_output_slots = {1, 2, 3, 4, 5, 6}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    upgrade_slot_start = 2
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        MixedProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MagmaCentrifugeUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.fluids = FluidSlotSync.ListFromMachine(self)
        self.sync.MarkedAsChanged()
