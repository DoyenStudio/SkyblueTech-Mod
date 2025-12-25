# coding=utf-8
#
from mod.server.blockEntityData import BlockEntityData
from ..define.events.freezer import FreezerModeChangedEvent
from ..define.id_enum.machinery import FREEZER as MACHINE_ID
from ..machinery_def.freezer import recipes as Recipes
from ..ui_sync.machines.freezer import FreezerUISync
from ..utils.action_commit import SafeGetMachine
from .basic import MixedProcessor, RegisterMachine

K_MODE = "mode"


@RegisterMachine
class Freezer(MixedProcessor):
    block_name = MACHINE_ID
    store_rf_max = 8800
    recipes = []
    output_slots = (0,)
    fluid_input_slots = {0}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (2000,)
    upgrade_slot_start = 1
    upgrade_slots = 4

    def __init__(self, dim, x, y, z, block_entity_data):
        # type: (int, int, int, int, BlockEntityData) -> None
        MixedProcessor.__init__(self, dim, x, y, z, block_entity_data)
        self.sync = FreezerUISync.NewServer(self).Activate()
        self.OnSync()

    def OnLoad(self):
        MixedProcessor.OnLoad(self)
        self.recipe_mode = self.bdata[K_MODE] or 0
        self.setMode(self.recipe_mode)

    def OnSync(self):
        self.sync.storage_rf = self.store_rf
        self.sync.rf_max = self.store_rf_max
        self.sync.progress_relative = self.GetProgressPercent()
        self.sync.fluid_id = self.fluids[0].fluid_id
        self.sync.fluid_volume = self.fluids[0].volume
        self.sync.max_volume = self.fluids[0].max_volume
        self.sync.freezer_mode = self.mode
        self.sync.MarkedAsChanged()

    def setMode(self, new_mode):
        # type: (int) -> None
        if new_mode >= len(Recipes):
            new_mode %= len(Recipes)
        self.recipes = [Recipes[new_mode]]
        self.mode = new_mode
        self.OnSync()
        self.StartNext()


@FreezerModeChangedEvent.Listen()
def onFreezerModeChanged(event):
    # type: (FreezerModeChangedEvent) -> None
    machine = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(machine, Freezer):
        return
    machine.setMode(event.new_mode)
    machine.sync.FastSync(event.player_id)

