# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..define.id_enum.machinery import OIL_EXTRACTOR as MACHINE_ID
from ..machinery_def.oil_extractor import recipes as Recipes
from ..ui_sync.machinery.oil_extractor import OilExtractorUISync
from .basic import MixedProcessor, RegisterMachine


@RegisterMachine
class OilExtractor(MixedProcessor):
    block_name = MACHINE_ID
    recipes = Recipes
    input_slots = (0,)
    output_slots = ()
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_output_slots = {0}
    fluid_slot_max_volumes = (1000,)
    upgrade_slot_start = 1

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        MixedProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = OilExtractorUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.fluid_id = self.fluids[0].fluid_id
        self.sync.fluid_volume = self.fluids[0].volume
        self.sync.max_volume = self.fluids[0].max_volume
        self.sync.MarkedAsChanged()
