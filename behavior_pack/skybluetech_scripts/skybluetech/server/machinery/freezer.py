# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.events.machinery.freezer import FreezerModeChangedEvent
from ...common.define.id_enum.machinery import Machinery
MACHINE_ID = Machinery.FREEZER
from ...common.mini_jei.core import RecipesCollection
from ...common.machinery_def.freezer import (
    recipes as Recipes,
    STORE_RF_MAX,
    MAX_FLUID_VOLUME,
    K_MODE,
)
from .utils.action_commit import SafeGetMachine
from .basic import MultiFluidContainer, Processor, RegisterMachine


@RegisterMachine
class Freezer(MultiFluidContainer, Processor):
    block_name = MACHINE_ID
    store_rf_max = STORE_RF_MAX
    dump_progress_to_block_entity_data = True
    process_item = True
    process_fluid = True
    recipes = RecipesCollection(MACHINE_ID)
    output_slots = (0,)
    fluid_input_slots = {0}
    fluid_io_mode = (0, 0, 0, 0, 0, 0)
    fluid_slot_max_volumes = (MAX_FLUID_VOLUME,)
    upgrade_slot_start = 1
    upgrade_slots = 4

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.set_mode(self.recipe_mode)

    @SuperExecutorMeta.execute_super
    def OnAddedFluid(self, slot, fluid_id, fluid_volume, is_final):
        pass

    @SuperExecutorMeta.execute_super
    def OnReducedFluid(self, slot, fluid_id, reduced_fluid_volume, is_final):
        pass

    def set_mode(self, new_mode):
        # type: (int) -> None
        if new_mode >= len(Recipes):
            new_mode %= len(Recipes)
        self.recipes = RecipesCollection(MACHINE_ID, Recipes.recipes_mapping[new_mode])
        self.recipe_mode = new_mode
        self.start_next()

    @property
    def recipe_mode(self):
        # type: () -> int
        return self.bdata[K_MODE] or 0

    @recipe_mode.setter
    def recipe_mode(self, value):
        # type: (int) -> None
        self.bdata[K_MODE] = value


@FreezerModeChangedEvent.Listen()
def onFreezerModeChanged(event):
    # type: (FreezerModeChangedEvent) -> None
    machine = SafeGetMachine(event.x, event.y, event.z, event.player_id)
    if not isinstance(machine, Freezer):
        return
    machine.set_mode(event.new_mode)
