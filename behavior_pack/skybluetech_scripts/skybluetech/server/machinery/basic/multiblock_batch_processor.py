# coding=utf-8
import json

from skybluetech_scripts.skybluetech.common.define import flags
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from .multi_block_structure import MultiBlockStructure
from .multi_fluid_container import MultiFluidContainer
from .multiblock_processing_ports import MultiblockProcessingPorts
from .processor import Processor
from .slot_reads import SlotReads, accepts_slot_reads


class MultiblockBatchProcessor(MultiblockProcessingPorts, Processor, MultiFluidContainer, MultiBlockStructure):
    """开工扣料、完工交付的多方块机器。子类提供配方类型、存档键和每步费用。"""

    work_units_per_tick = 1
    work_key = None
    refresh_ports_on_sync = True
    sync_on_work_tick = False

    def __init__(self, dim, x, y, z, block_entity_data):
        saved = block_entity_data[self.batch_key]
        # Processor 构造时会选方，必须先恢复已投料批次。
        self._batch = self.batch_recipe_type.Unmarshal(json.loads(saved)) if saved else None
        self._work = 0
        self._advancing = False
        super(MultiblockBatchProcessor, self).__init__(dim, x, y, z, block_entity_data)
        if self._batch is None:
            self.recheck_recipe()
        else:
            self.bdata[self.recipe_id_key] = self._batch.recipe_id
            if self.work_key is None:
                self._work = int((self._batch.tick_duration - self.ticks_left) * self.work_units_per_tick)
            else:
                self._work = int(block_entity_data[self.work_key] or 0)
                self._update_ticks_left()
        self._init_ios(refresh_on_sync=self.refresh_ports_on_sync)
        self._last_work_status = None
        self._update_work_status()

    @accepts_slot_reads
    def get_recipe(self, slot_reads=None):
        if self._batch is not None:
            return 0, self._batch
        return super(MultiblockBatchProcessor, self).get_recipe(slot_reads=slot_reads)

    def recheck_recipe(self):
        if self._batch is not None or self._applying_recipe:
            return
        _, recipe = self.get_recipe()
        self.current_recipe = recipe
        self._output_dirty = True
        self.bdata[self.recipe_id_key] = recipe.recipe_id if recipe else ""
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE, recipe is None)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        if recipe is None:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        else:
            self.SetProcessTicks(recipe.tick_duration)
            self.SetPower(recipe.power_cost)
        self.ResetProgress()

    def _base_speed_control_set_deactive_flag(self, flag, flush=True):
        if self._batch is None:
            super(MultiblockBatchProcessor, self)._base_speed_control_set_deactive_flag(flag, flush)

    def _begin_batch(self, recipe):
        reads = SlotReads(self)
        _, actual = reads.call(self.get_recipe)
        if actual is not recipe or not reads.call(self.can_output, recipe):
            self.recheck_recipe()
            return False
        self._batch = recipe
        if not reads.call(self._apply_recipe, recipe, consume_inputs=True, produce_outputs=False):
            self._batch = None
            self.recheck_recipe()
            return False
        self.bdata[self.batch_key] = json.dumps(recipe.Marshal(), ensure_ascii=True)
        self._set_work(0)
        self.transmit_materials()
        return True

    def run_once(self):
        if self._batch is None or self.ticks_left > 0:
            return False
        if not self._apply_recipe(self._batch, consume_inputs=False, produce_outputs=True):
            self._output_dirty = True
            return False
        self._batch = self.bdata[self.batch_key] = None
        self._set_work(0)
        self.recheck_recipe()
        self.transmit_materials()
        return True

    def _set_work(self, work):
        self._work = work
        if self.work_key is not None:
            self.bdata[self.work_key] = work

    def _update_ticks_left(self):
        remaining = self._batch.tick_duration * self.work_units_per_tick - self._work
        self.ticks_left = remaining if self.work_units_per_tick == 1 else remaining / float(self.work_units_per_tick)

    def _processor_on_ticking(self):
        self._io_refresh_ticks += 1
        if self._io_refresh_ticks >= 20:
            self._io_refresh_ticks = 0
            self._refresh_io_bindings()
        self._advancing = False
        finished = self.ProcessOnce()
        if finished:
            self.run_once()
        self._update_work_status()
        if self.sync_on_work_tick and (self._advancing or finished):
            self.CallSync()

    def ProcessOnce(self):
        recipe = self.current_recipe
        if recipe is None or not self.StructureFinished():
            return False
        if self._output_dirty:
            self._check_output()
        remaining = recipe.tick_duration * self.work_units_per_tick - self._work
        step, charge = self._batch_step_and_cost(recipe, remaining)
        self.SetPower(charge)
        if not self.PowerEnough() or not self.IsActive():
            return False
        if self._batch is None and not self._begin_batch(recipe):
            return False
        if step:
            self.ReducePower(charge, bypass_upgraders=True)
            self._advance_work(recipe, step)
            self._advancing = True
        return step == remaining

    def _batch_step_and_cost(self, recipe, remaining):
        """返回本 tick 推进的工作量和应扣 RF，remaining 和步长均按 work_units_per_tick 计。"""
        raise NotImplementedError

    def _advance_work(self, recipe, step):
        self._set_work(self._work + step)
        self._update_ticks_left()

    def _update_work_status(self, flush=True):
        if not flush:
            return
        active = self._advancing and self._batch is not None and self.IsActive() and self.StructureFinished()
        if active == self._last_work_status:
            return
        comp = CF.CreateBlockState(LEVEL_ID)
        states = comp.GetBlockStates(self.xyz, self.dim)
        if states is not None:
            states["skybluetech:active"] = active
            comp.SetBlockStates(self.xyz, states, self.dim)
            self._last_work_status = active
            self.handler.CallOnWorkStatusUpdatedHandlers()
