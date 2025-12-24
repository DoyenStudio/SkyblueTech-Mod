# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..machinery_def.alloy_furnace import recipes as Recipes
from ..ui_sync.machines.alloy_furnace import AlloyFurnaceUISync
from .basic import BaseProcessor, RegisterMachine


@RegisterMachine
class AlloyFurnace(BaseProcessor):
    block_name = "skybluetech:alloy_furnace"
    store_rf_max = 8800
    recipes = Recipes
    input_slots = (0, 1, 2, 3)
    output_slots = (4, 5)
    upgrade_slot_start = 6

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        BaseProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = AlloyFurnaceUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.MarkedAsChanged()

