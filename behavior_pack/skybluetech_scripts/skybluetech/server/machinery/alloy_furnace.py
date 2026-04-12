# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import ALLOY_FURNACE as MACHINE_ID
from ...common.machinery_def.alloy_furnace import recipes as Recipes
from ...common.ui_sync.machinery.alloy_furnace import AlloyFurnaceUISync
from .basic import Processor, RegisterMachine


@RegisterMachine
class AlloyFurnace(Processor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    process_item = True
    recipes = Recipes
    input_slots = (0, 1, 2, 3)
    output_slots = (4, 5)
    upgrade_slot_start = 6

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = AlloyFurnaceUISync.NewServer(self).Activate()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.MarkedAsChanged()
