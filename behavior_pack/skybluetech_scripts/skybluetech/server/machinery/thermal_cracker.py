# coding=utf-8
import json

from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.facing import RelFacEnum
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.thermal_cracker import (
    CHAMBER_HEAT_CAPACITY, FLUID_SLOT_MAX_VOLUMES, K_BATCH, K_BATCH_PROGRESS, K_BATCH_WORK, recipes,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.multi_fluid_container import FLUID_VOLUME_EPSILON
from skybluetech_scripts.skybluetech.common.mini_jei.core import CategoryType
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.thermal_cracker import ThermalCrackerRecipe
from skybluetech_scripts.skybluetech.server.machinery.basic import GUIControl, HeatCtrl, ItemContainer, MultiFluidContainer
from skybluetech_scripts.skybluetech.server.machinery.basic.fluid_output_faces import FluidOutputFaces
from skybluetech_scripts.skybluetech.server.machinery.basic.work_renderer import WorkRenderer
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

IDLE_FLAGS = (
    flags.DEACTIVE_FLAG_NO_INPUT, flags.DEACTIVE_FLAG_NO_RECIPE, flags.DEACTIVE_FLAG_HEAT_LACK,
    flags.DEACTIVE_FLAG_OUTPUT_FULL, flags.DEACTIVE_FLAG_FLUID_FULL, flags.DEACTIVE_FLAG_FLUID_NOT_MATCH,
)
IDLE_MASK = 0
for _flag in IDLE_FLAGS:
    IDLE_MASK |= _flag
_WORK_UNITS_PER_TICK = 256


@RegisterMachine
class ThermalCracker(FluidOutputFaces, WorkRenderer, GUIControl, ItemContainer, MultiFluidContainer, HeatCtrl):
    block_name = Machinery.THERMAL_CRACKER
    heat_input_faces = (RelFacEnum.DOWN,)
    is_non_energy_machine = True
    heat_capacity = CHAMBER_HEAT_CAPACITY
    item_input_slots = (0,)
    item_output_slots = (1,)
    fluid_input_slots = (0, 1)
    fluid_output_slots = (2, 3)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_output_slots_by_face = {
        RelativeFacingStrEnum.LEFT: (2,), RelativeFacingStrEnum.RIGHT: (3,),
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ThermalCracker, self).__init__(dim, x, y, z, block_entity_data)
        saved = self.bdata[K_BATCH]
        self._batch = ThermalCrackerRecipe.Unmarshal(json.loads(saved)) if saved else None
        self._batch_work = int(self.bdata[K_BATCH_WORK] or 0) if self._batch else 0
        self._working = False
        self.handler.SubscribeOnTicking(self._cracker_on_tick)

    def IsValidInput(self, slot, item):
        return slot == 0 and any(
            recipe.recipe_id and recipe.inputs[CategoryType.ITEM][0].match_item_id(item.id, item.newAuxValue)
            for recipe in recipes
        )

    def IsValidFluidInput(self, slot, fluid_id):
        return slot in self.fluid_input_slots and any(
            slot < len(recipe.input_fluids) and recipe.input_fluids[slot][0] == fluid_id
            for recipe in recipes
        )

    def _cracker_on_tick(self):
        if self._working or not self.IsActiveIgnoreCondition(IDLE_MASK):
            return
        self._working = True
        try:
            reason = self.work_once()
            if reason:
                self.UpdateDeactiveFlag(reason, True)
            for flag in IDLE_FLAGS:
                if flag != reason:
                    self.UpdateDeactiveFlag(flag, False)
            self.CallSync()
        finally:
            self._working = False

    def work_once(self):
        if self._batch is not None:
            return self._work_batch(self._batch)
        primary = self.fluids[0]
        primary_fluid = primary.fluid_id
        if primary_fluid is None:
            return flags.DEACTIVE_FLAG_NO_INPUT
        secondary = self.fluids[1]
        batch_candidates = []
        for recipe in recipes:
            if recipe.input_fluids[0][0] != primary_fluid:
                continue
            if recipe.recipe_id:
                batch_candidates.append(recipe)
            elif secondary.fluid_id == recipe.input_fluids[1][0]:
                return self._commit_recipe(recipe)
        if not batch_candidates:
            return flags.DEACTIVE_FLAG_NO_INPUT
        item = self.GetSlotItem(0)
        if item is None:
            return flags.DEACTIVE_FLAG_NO_INPUT
        reason = flags.DEACTIVE_FLAG_NO_RECIPE
        for recipe in batch_candidates:
            if not recipe.inputs[CategoryType.ITEM][0].match_item_id(item.id, item.newAuxValue):
                continue
            if (
                item.count >= recipe.solid_in[1]
                and primary.volume >= recipe.input_fluids[0][1]
                and all(secondary.fluid_id == fluid_id and secondary.volume >= volume
                        for fluid_id, volume in recipe.input_fluids[1:])
            ):
                return self._work_batch(recipe, item)
            reason = flags.DEACTIVE_FLAG_NO_INPUT
        return reason

    def _begin_batch(self, recipe, item):
        item.count -= recipe.solid_in[1]
        if not self.SetSlotItem(0, item if item.count else None):
            return False
        self._batch = recipe
        self.bdata[K_BATCH] = json.dumps(recipe.Marshal(), ensure_ascii=True)
        self._set_batch_work(0, recipe.tick_duration * _WORK_UNITS_PER_TICK)
        for slot, (_, volume) in enumerate(recipe.input_fluids):
            self.fluids[slot].volume -= volume
        for slot, (fluid_id, volume) in enumerate(recipe.input_fluids):
            self._on_reduced_fluid(slot, fluid_id, volume, slot == len(recipe.input_fluids) - 1)
        return True

    def _set_batch_work(self, units, total):
        self._batch_work = self.bdata[K_BATCH_WORK] = units
        self.bdata[K_BATCH_PROGRESS] = units / float(total)

    def _work_batch(self, recipe, input_item=None):
        total = recipe.tick_duration * _WORK_UNITS_PER_TICK
        remaining = total - self._batch_work
        step = 0
        if remaining > 0:
            speed_units = int(recipe.speed_at(self.kelvin) * _WORK_UNITS_PER_TICK)
            spare_heat = self.heat_value - self.heat_capacity * recipe.min_temperature
            heat_units = int(spare_heat * total / recipe.heat_cost)
            step = min(remaining, speed_units, heat_units)
            if step <= 0:
                return flags.DEACTIVE_FLAG_HEAT_LACK

        for slot, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            target = self.fluids[slot]
            if target.fluid_id not in (None, fluid_id):
                return flags.DEACTIVE_FLAG_FLUID_NOT_MATCH
            if target.max_volume - target.volume < volume:
                return flags.DEACTIVE_FLAG_FLUID_FULL
        output_id, count = recipe.solid_out
        product = Item(output_id, count=count)
        existing = self.GetSlotItem(1)
        if existing is not None and (
            not existing.CanMerge(product) or existing.count + count > existing.GetBasicInfo().maxStackSize
        ):
            return flags.DEACTIVE_FLAG_OUTPUT_FULL

        if input_item is not None and not self._begin_batch(recipe, input_item):
            return flags.DEACTIVE_FLAG_NO_INPUT
        if step:
            self.heat_value -= recipe.heat_cost * step / float(total)
            self._set_batch_work(self._batch_work + step, total)
        if step < remaining:
            return 0
        if existing is not None:
            existing.count += count
            product = existing
        if not self.SetSlotItem(1, product):
            return flags.DEACTIVE_FLAG_OUTPUT_FULL
        for slot, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            self.fluids[slot].fluid_id = fluid_id
            self.fluids[slot].volume += volume
        self._batch = self.bdata[K_BATCH] = None
        self._set_batch_work(0, total)
        for slot, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            self._on_added_fluid(slot, fluid_id, volume, slot == 1 + len(recipe.output_fluids))
        return 0

    def _commit_recipe(self, recipe):
        scale = recipe.speed_at(self.kelvin) / float(recipe.tick_duration)
        scale = min(scale, (self.heat_value - self.heat_capacity * recipe.min_temperature) / recipe.heat_cost)
        for i, (fluid_id, volume) in enumerate(recipe.input_fluids):
            scale = min(scale, self.fluids[i].volume / volume)
        if any(volume * scale <= FLUID_VOLUME_EPSILON
               for _, volume in recipe.input_fluids + recipe.output_fluids):
            return flags.DEACTIVE_FLAG_NO_RECIPE
        for i, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            target = self.fluids[i]
            if target.fluid_id not in (None, fluid_id):
                return flags.DEACTIVE_FLAG_FLUID_NOT_MATCH
            if target.max_volume - target.volume < volume * scale:
                return flags.DEACTIVE_FLAG_FLUID_FULL
        # Commit all four inventories and heat before notifying any observers.
        for i, (fluid_id, volume) in enumerate(recipe.input_fluids):
            self.fluids[i].volume -= volume * scale
        for i, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            self.fluids[i].fluid_id = fluid_id
            self.fluids[i].volume += volume * scale
        self.heat_value -= recipe.heat_cost * scale
        for i, (fluid_id, volume) in enumerate(recipe.input_fluids):
            self._on_reduced_fluid(i, fluid_id, volume * scale, True)
        for i, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            self._on_added_fluid(i, fluid_id, volume * scale, True)
        return 0
