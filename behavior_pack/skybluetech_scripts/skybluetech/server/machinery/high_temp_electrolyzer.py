# coding=utf-8
from math import ceil

from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.skybluetech.common.define.facing import RelFacEnum
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery
from skybluetech_scripts.skybluetech.common.machinery_def import high_temp_electrolyzer as definition
from skybluetech_scripts.skybluetech.server.machinery.basic import HeatCtrl, MultiFluidContainer, Processor
from skybluetech_scripts.skybluetech.server.machinery.basic.fluid_output_faces import FluidOutputFaces
from skybluetech_scripts.skybluetech.server.machinery.basic.slot_reads import SlotReads, accepts_slot_reads
from skybluetech_scripts.skybluetech.server.machinery.core import RegisterMachine


@RegisterMachine
class HighTempElectrolyzer(FluidOutputFaces, Processor, MultiFluidContainer, HeatCtrl):
    block_name = Machinery.HIGH_TEMP_ELECTROLYZER
    recipes = definition.recipes
    store_rf_max = definition.STORE_RF_MAX
    process_item = process_fluid = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    upgrade_slot_start = 2
    upgrade_slots = 4
    fluid_input_slots = (0,)
    fluid_output_slots = (1,)
    fluid_output_slots_by_face = {RelFacEnum.RIGHT: (1,)}
    fluid_slot_max_volumes = definition.FLUID_SLOT_MAX_VOLUMES
    fluid_io_mode = (-1,) * 6
    heat_input_faces = (RelFacEnum.DOWN,)
    heat_output_faces = ()

    def __init__(self, dim, x, y, z, block_entity_data):
        self._batch_id = block_entity_data[definition.K_BATCH] or ""
        super(HighTempElectrolyzer, self).__init__(dim, x, y, z, block_entity_data)
        if self._remember_batch():
            self.ResetProgress()

    @accepts_slot_reads
    def get_recipe(self, slot_reads=None):
        # 两种进料可同时留在机器内。补入另一种原料或读档时优先续做原批。
        reads = slot_reads or SlotReads(self)
        for index, recipe in enumerate(self.recipes):
            if (recipe.recipe_id == self._batch_id
                    and reads.allocate_inputs(recipe) is not None
                    and reads.allocate_fluid_inputs(recipe) is not None):
                return index, recipe
        return Processor.get_recipe(self, reads)

    def _remember_batch(self):
        batch_id = self.current_recipe.recipe_id if self.current_recipe else ""
        if self._batch_id == batch_id:
            return False
        self._batch_id = self.bdata[definition.K_BATCH] = batch_id
        return True

    def start_next(self, _recipe=None, check_power=True):
        Processor.start_next(self, _recipe, check_power)
        self._remember_batch()

    def recheck_recipe(self):
        Processor.recheck_recipe(self)
        self._remember_batch()

    def _processor_on_ticking(self):
        recipe = self.current_recipe
        cold = recipe is not None and self.kelvin < recipe.min_temperature
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK, cold)
        if recipe is None:
            return
        if not cold:
            fraction = min(1.0, (self.kelvin - recipe.min_temperature)
                           / float(recipe.fit_temperature - recipe.min_temperature))
            # 二进制小数可在方块存档中精确保存，临界温度从最小一步起步。
            step = max(1, int(256 * self.reduce_ticks * fraction)) / 256.0
            self._step = min(self.ticks_left, step)
            done = recipe.tick_duration - self.ticks_left
            unit_cost = recipe.power_cost * self._power_cost_relative / self.reduce_ticks
            self._charge = int(ceil((done + self._step) * unit_cost) - ceil(done * unit_cost))
            self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK, self.store_rf < self._charge)
        Processor._processor_on_ticking(self)

    def ProcessOnce(self):
        recipe = self.current_recipe
        self.ReducePower(self._charge, bypass_upgraders=True)
        self.heat_value -= recipe.heat_cost * self._step / recipe.tick_duration
        self.ticks_left -= self._step
        return self.ticks_left <= 0
