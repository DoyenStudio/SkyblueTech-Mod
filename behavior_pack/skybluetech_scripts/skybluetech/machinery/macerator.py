# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..machinery_def.macerator import recipes as Recipes
from ..ui_sync.machines.macerator import MaceratorUISync
from .basic import RegisterMachine, BaseProcessor


@RegisterMachine
class Macerator(BaseProcessor):
    block_name = "skybluetech:macerator"
    store_rf_max = 8800
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MaceratorUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.MarkedAsChanged()

