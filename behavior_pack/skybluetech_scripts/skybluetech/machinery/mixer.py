# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..machinery_def.mixer import recipes as Recipes, MachineRecipe
from ..ui_sync.machines.mixer import MixerUISync
from .basic import MixedProcessor, RegisterMachine


@RegisterMachine
class Mixer(MixedProcessor):
    block_name = "skybluetech:mixer"
    store_rf_max = 8800
    recipes = Recipes
    input_slots = (0,)
    output_slots = (1,)
    fluid_input_slots = {0}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (2000,)

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        MixedProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = MixerUISync.NewServer(self).Activate()
        self.OnSync()

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.fluid_id = self.fluids[0].fluid_id
        self.sync.fluid_volume = self.fluids[0].volume
        self.sync.max_volume = self.fluids[0].max_volume
        self.sync.MarkedAsChanged()

