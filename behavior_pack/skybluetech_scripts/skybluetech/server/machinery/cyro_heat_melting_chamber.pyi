# coding=utf-8
from skybluetech_scripts.tooldelta.internal import GetServer
from .basic.multi_fluid_container import MultiFluidContainer
from skybluetech_scripts.tooldelta.define import Item

from ...common.define.id_enum.machinery import CYRO_HEAT_MELTING_CHAMBER as MACHINE_ID
from ...common.machinery_def.cyro_heat_melting_chamber import (
    recipes as Recipes,
    CyroHeatMeltingChamberRecipe,
)
from ...common.ui_sync.machinery.cyro_heat_melting_chamber import (
    CyroHeatMeltingChamberUISync,
)
from .basic import (
    HeatCtrl,
    GUIControl,
    ItemContainer,
)
from .core import RegisterMachine
from .utils.production import OutputRecipe, FlushRecipeStat

K_WORKING_TICKS = "st:working_ticks"
K_CURRENT_MIN_TEMPERATURE = "st:current_min_temperature"
K_CURRENT_FIT_TEMPERATURE = "st:current_fit_temperature"
K_CURRENT_MAX_TEMPERATURE = "st:current_max_temperature"

@RegisterMachine
class CyroHeatMeltingChamber(ItemContainer, GUIControl, MultiFluidContainer, HeatCtrl):
    block_name = MACHINE_ID
    is_non_energy_machine = True
    fluid_io_fix_mode = 0
    fluid_slot_max_volumes = {0: 1000}
    fluid_input_slots = (0,)
    fluid_output_slots = (0,)
    migrate_legacy_fluid_data = True

    def __init__(self, dim, x, y, z, block_entity_data):
        super(CyroHeatMeltingChamber, self).__init__(dim, x, y, z, block_entity_data)
        self.sync = CyroHeatMeltingChamberUISync.NewServer(self).Activate()
        self.t = 0
        self.produce_speed = 0
        self.max_process_ticks = 1
        self.current_recipe = None
        self._working_ticks = block_entity_data[K_WORKING_TICKS]
        self.flush_recipe()
        self.handler.SubscribeOnTicking(self._cyro_heat_melting_chamber_on_ticking)
        self.handler.SubscribeOnSync(self._cyro_heat_melting_chamber_on_sync)
        self.handler.SubscribeOnSlotUpdate(self._cyro_heat_melting_chamber_on_slot_update)
        self.CallSync()


    def _cyro_heat_melting_chamber_on_ticking(self):
        if self.IsActive():
            self.flush_produce_speed()
            self.work_once()
            self.CallSync()

    def _cyro_heat_melting_chamber_on_sync(self):
        # type: () -> None
        self.sync.current_temperature = self.kelvin
        self.sync.produce_speed = self.produce_speed
        self.sync.progress = self.working_ticks * 1.0 / self.max_process_ticks
        self.sync.MarkedAsChanged()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        results = (
            MultiFluidContainer.IsValidFluidInput(self, slot, fluid_id),
            self._cyro_heat_melting_chamber_is_valid_fluid_input(slot, fluid_id),
        )
        return all(results)

    def _cyro_heat_melting_chamber_is_valid_fluid_input(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id in Recipes.recipes_mapping

    def _cyro_heat_melting_chamber_on_slot_update(self, slot_pos):
        # type: (int) -> None
        if slot_pos != 0:
            return
        self.flush_recipe()

    def IsValidInput(self, slot, item):
        # type: (int, Item) -> bool
        results = (
            ItemContainer.IsValidInput(self, slot, item),
            self._cyro_heat_melting_chamber_is_valid_input(slot, item),
        )
        return all(results)

    def _cyro_heat_melting_chamber_is_valid_input(self, slot, item):
        # type: (int, Item) -> bool
        return slot == 0 and item.id in Recipes.recipes_mapping

    def work_once(self):
        self.t += 1
        self.working_ticks += self.produce_speed
        if self.working_ticks >= self.max_process_ticks:
            self.finish_recipe()
        if self.t % 5 == 0:
            self.heat_value -= 1

    def flush_recipe(self):
        last_recipe = self.current_recipe
        self.current_recipe = None
        input_item = self.GetSlotItem(0)
        if input_item is None:
            return
        self.current_recipe = Recipes.recipes_mapping.get(input_item.id)
        if FlushRecipeStat(self.current_recipe, self):
            if self.current_recipe != last_recipe:
                self.working_ticks = 0
            self.max_process_ticks = self.current_recipe.tick_duration
            self.flush_produce_speed()

    def flush_produce_speed(self):
        # type: () -> None
        if self.current_recipe is None:
            return
        T = self.kelvin
        T_min = self.current_recipe.min_temperature
        T_fit = self.current_recipe.fit_temperature
        T_max = self.current_recipe.max_temperature
        self.produce_speed = (
            self.current_recipe.max_tick_speed
            * 1.0
            * max(0, min(T, T_max) - T_min)
            / (T_fit - T_min)
        )

    def finish_recipe(self):
        # type: () -> None
        self.flush_recipe()
        recipe = self.current_recipe
        if recipe is None:
            return
        if self.kelvin <= recipe.max_temperature:
            OutputRecipe(self, recipe)
        elif recipe.waste is not None:
            GetServer().CreateEngineItemEntity(
                Item(recipe.waste).marshal(),
                self.dim,
                (self.x + 0.5, self.y + 0.5, self.z + 0.5),
            )
        self.working_ticks = 0

    @property
    def working_ticks(self):
        return self._working_ticks

    @working_ticks.setter
    def working_ticks(self, value):
        self._working_ticks = value
        self.bdata[K_WORKING_TICKS] = value
