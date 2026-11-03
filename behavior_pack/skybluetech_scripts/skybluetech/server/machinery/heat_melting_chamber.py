# coding=utf-8
from ...common.define import flags
from skybluetech_scripts.skybluetech.common.define.facing import RelFacEnum
from ...common.define.id_enum import Machinery
from ...common.machinery_def.heat_melting_chamber import (
    CHAMBER_HEAT_CAPACITY, OUTPUT_MAX_VOLUME, K_PROGRESS, K_RECIPE_INPUT,
    K_SPEED, K_DURATION, K_OVERHEATED, recipes,
)
from .basic import GUIControl, HeatCtrl, ItemContainer, MultiFluidContainer
from .core import RegisterMachine
from .utils.production import MachineRecipeCanOutput, OutputRecipe

IDLE_FLAGS = (flags.DEACTIVE_FLAG_NO_INPUT, flags.DEACTIVE_FLAG_NO_RECIPE,
              flags.DEACTIVE_FLAG_OUTPUT_FULL)


@RegisterMachine
class HeatMeltingChamber(ItemContainer, GUIControl, MultiFluidContainer, HeatCtrl):
    block_name = Machinery.HEAT_MELTING_CHAMBER
    heat_faces_follow_rotation = False
    heat_input_faces = (RelFacEnum.DOWN,)
    is_non_energy_machine = True
    heat_capacity = CHAMBER_HEAT_CAPACITY
    item_input_slots = (0,)
    item_output_slots = (1,)
    fluid_io_mode = (1, 1, 1, 1, 1, 1)
    fluid_input_slots = ()
    fluid_output_slots = (0,)
    fluid_slot_max_volumes = {0: OUTPUT_MAX_VOLUME}

    def __init__(self, dim, x, y, z, block_entity_data):
        super(HeatMeltingChamber, self).__init__(dim, x, y, z, block_entity_data)
        self.progress = float(self.bdata[K_PROGRESS] or 0.0)
        self.recipe_input = self.bdata[K_RECIPE_INPUT]
        self.handler.SubscribeOnTicking(self._on_melting_tick)

    def IsValidInput(self, slot, item):
        return slot == 0 and any(r.input_item_id == item.id for r in recipes)

    def _on_melting_tick(self):
        item = self.GetSlotItem(0)
        recipe = next((r for r in recipes if item is not None
                       and r.input_item_id == item.id), None)
        recipe_input = recipe.input_item_id if recipe else None
        if recipe_input != self.recipe_input:
            self.progress = 0.0
            self.recipe_input = recipe_input
        temperature = self.kelvin
        speed = 0.0
        overheated = False
        reason = 0
        effective_recipe = None
        if item is None:
            reason = flags.DEACTIVE_FLAG_NO_INPUT
        elif recipe is None or temperature <= recipe.min_temperature:
            reason = flags.DEACTIVE_FLAG_NO_RECIPE
        else:
            overheated = temperature > recipe.max_temperature
            effective_recipe = recipe.overheated_recipe if overheated else recipe
            if not MachineRecipeCanOutput(self, effective_recipe):
                reason = flags.DEACTIVE_FLAG_OUTPUT_FULL
            else:
                speed = min(1.0, (temperature - recipe.min_temperature)
                            / float(recipe.fit_temperature - recipe.min_temperature))
        for flag in IDLE_FLAGS:
            self.UpdateDeactiveFlag(flag, reason == flag)
        if effective_recipe is not None and self.IsActive() and speed > 0:
            step = min(speed, max(0.0, recipe.tick_duration - self.progress))
            heat_per_tick = recipe.output_volume * recipe.heat_per_produce / float(recipe.tick_duration)
            if heat_per_tick > 0:
                step = min(step, self.heat_value / heat_per_tick)
            self.heat_value -= step * heat_per_tick
            self.progress += step
            if self.progress >= recipe.tick_duration:
                # 所有产出已预检；先消耗一个输入，避免重复加工。
                item.count -= 1
                if self.SetSlotItem(0, item if item.count > 0 else None):
                    OutputRecipe(self, effective_recipe)
                    self.progress = 0.0
        else:
            speed = 0.0
        self.bdata[K_PROGRESS] = float(self.progress)
        self.bdata[K_RECIPE_INPUT] = self.recipe_input
        self.bdata[K_SPEED] = float(speed)
        self.bdata[K_DURATION] = float(recipe.tick_duration if recipe else 1.0)
        self.bdata[K_OVERHEATED] = overheated
        self.CallSync()
