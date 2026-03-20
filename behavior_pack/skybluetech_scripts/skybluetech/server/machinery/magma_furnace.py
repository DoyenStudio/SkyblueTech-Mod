# coding=utf-8
from ...common.define.id_enum.machinery import MAGMA_FURNACE as MACHINE_ID
from ...common.machinery_def.magma_furnace import recipes as Recipes
from ...common.ui_sync.machinery.magma_furnace import MagmaFurnaceUISync
from .basic import MixedProcessor, RegisterMachine


@RegisterMachine
class MagmaFurnace(MixedProcessor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    recipes = Recipes
    origin_process_ticks = 20 * 8  # 8s
    input_slots = (0,)
    output_slots = (1,)
    fluid_slot_max_volumes = (4000,)
    upgrade_slot_start = 2
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        MixedProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MagmaFurnaceUISync.NewServer(self).Activate()
        self.CallSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProcessProgress()
        f = self.fluids[0]
        self.sync.fluid_id = f.fluid_id
        self.sync.fluid_volume = f.volume
        self.sync.max_volume = f.max_volume
        self.sync.MarkedAsChanged()
