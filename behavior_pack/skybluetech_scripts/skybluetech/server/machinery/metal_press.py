# coding=utf-8
from ...common.define.id_enum.machinery import METAL_PRESS as MACHINE_ID
from ...common.machinery_def.metal_press import recipes as Recipes
from ...common.ui_sync.machinery.metal_press import MetalPressUISync
from .basic import MixedProcessor, RegisterMachine


@RegisterMachine
class MetalPress(MixedProcessor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    fluid_input_slots = {0}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (2000,)

    def __init__(self, dim, x, y, z, block_entity_data):
        MixedProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MetalPressUISync.NewServer(self).Activate()
        self.CallSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.fluid_id = self.fluids[0].fluid_id
        self.sync.fluid_volume = self.fluids[0].volume
        self.sync.max_volume = self.fluids[0].max_volume
        self.sync.MarkedAsChanged()
