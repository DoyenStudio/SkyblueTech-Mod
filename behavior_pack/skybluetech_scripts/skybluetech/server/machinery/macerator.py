# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import MACERATOR as MACHINE_ID
from ...common.machinery_def.macerator import recipes as Recipes
from ...common.ui_sync.machinery.macerator import MaceratorUISync
from .basic import RegisterMachine, BaseProcessor


@RegisterMachine
class Macerator(BaseProcessor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = MaceratorUISync.NewServer(self).Activate()
        self.CallSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.MarkedAsChanged()
