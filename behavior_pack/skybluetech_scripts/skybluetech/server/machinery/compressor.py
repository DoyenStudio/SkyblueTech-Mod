# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import COMPRESSOR as MACHINE_ID
from ...common.machinery_def.compressor import recipes as Recipes
from ...common.ui_sync.machinery.compressor import CompressorUISync
from .basic import RegisterMachine, Processor


@RegisterMachine
class Compressor(Processor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    process_item = True
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = CompressorUISync.NewServer(self).Activate()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.MarkedAsChanged()
