# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def.thermal_cracker import (
    CHAMBER_HEAT_CAPACITY, FLUID_SLOT_MAX_VOLUMES, recipes,
)
from skybluetech_scripts.skybluetech.common.machinery_def.basic.multi_fluid_container import FLUID_VOLUME_EPSILON
from skybluetech_scripts.skybluetech.server.machinery.basic import GUIControl, HeatCtrl, MultiFluidContainer
from skybluetech_scripts.skybluetech.server.machinery.basic.work_renderer import WorkRenderer
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

IDLE_FLAGS = (flags.DEACTIVE_FLAG_NO_INPUT, flags.DEACTIVE_FLAG_NO_RECIPE,
              flags.DEACTIVE_FLAG_FLUID_FULL, flags.DEACTIVE_FLAG_FLUID_NOT_MATCH)
IDLE_MASK = 0
for _flag in IDLE_FLAGS:
    IDLE_MASK |= _flag


@RegisterMachine
class ThermalCracker(WorkRenderer, GUIControl, MultiFluidContainer, HeatCtrl):
    block_name = Machinery.THERMAL_CRACKER
    is_non_energy_machine = True
    heat_capacity = CHAMBER_HEAT_CAPACITY
    fluid_input_slots = (0, 1)
    fluid_output_slots = (2, 3)
    fluid_slot_max_volumes = FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1, -1, -1, -1, -1, -1)
    fluid_output_slots_by_face = {
        RelativeFacingStrEnum.LEFT: (2,), RelativeFacingStrEnum.RIGHT: (3,),
    }

    def __init__(self, dim, x, y, z, block_entity_data):
        super(ThermalCracker, self).__init__(dim, x, y, z, block_entity_data)
        self._working = False
        self.handler.SubscribeOnTicking(self._cracker_on_tick)

    def IsValidFluidInput(self, slot, fluid_id):
        return slot in self.fluid_input_slots and any(
            recipe.input_fluids[slot][0] == fluid_id for recipe in recipes)

    def _cracker_on_tick(self):
        if self._working or not self.IsActiveIgnoreCondition(IDLE_MASK):
            return
        self._working = True
        try:
            reason = self.work_once()
            for flag in IDLE_FLAGS:
                self.UpdateDeactiveFlag(flag, reason == flag)
            self.CallSync()
        finally:
            self._working = False

    def work_once(self):
        for recipe in recipes:
            if all(self.fluids[i].fluid_id == fid and self.fluids[i].volume > FLUID_VOLUME_EPSILON
                   for i, (fid, volume) in enumerate(recipe.input_fluids)):
                return self._commit_recipe(recipe)
        return flags.DEACTIVE_FLAG_NO_INPUT

    def _commit_recipe(self, recipe):
        scale = recipe.speed_at(self.kelvin) / float(recipe.tick_duration)
        scale = min(scale, max(0.0, self.heat_value - self.heat_capacity * recipe.min_temperature) / recipe.heat_cost)
        for i, (fluid_id, volume) in enumerate(recipe.input_fluids):
            scale = min(scale, self.fluids[i].volume / volume)
        if scale <= 0 or any(volume * scale <= FLUID_VOLUME_EPSILON
                             for fluid_id, volume in recipe.input_fluids + recipe.output_fluids):
            return flags.DEACTIVE_FLAG_NO_RECIPE
        for i, (fluid_id, volume) in enumerate(recipe.output_fluids, 2):
            target = self.fluids[i]
            if target.fluid_id not in (None, fluid_id):
                return flags.DEACTIVE_FLAG_FLUID_NOT_MATCH
            if target.isFull() or target.max_volume - target.volume < volume * scale:
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
