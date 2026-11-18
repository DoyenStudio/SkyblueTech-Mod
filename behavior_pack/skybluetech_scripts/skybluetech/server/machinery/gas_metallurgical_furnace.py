# coding=utf-8
import json

from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from ...common.define import flags
from ...common.define.id_enum import GasMetallurgicalFurnace as ids
from ...common.machinery_def import gas_metallurgical_furnace as definition
from ...common.mini_jei.machinery.gas_metallurgical_furnace import GasMetallurgicalFurnaceRecipe
from .basic import Processor, MultiFluidContainer, MultiBlockStructure
from .basic.slot_reads import SlotReads, accepts_slot_reads
from .core import RegisterMachine
from .gas_metallurgical_furnace_io import GasFurnaceIO, PORTS


@RegisterMachine
class GasMetallurgicalFurnace(GasFurnaceIO, Processor, MultiFluidContainer, MultiBlockStructure):
    block_name = ids.CONTROLLER
    store_rf_max = definition.STORE_RF_MAX
    recipes = definition.recipes
    process_item = True
    process_fluid = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    item_input_slots_by_face = {}
    item_output_slots_by_face = {}
    energy_io_mode = (2, 2, 2, 2, 2, 2)
    fluid_input_slots = (0, 1, 2)
    fluid_output_slots = (3, 4)
    fluid_slot_max_volumes = definition.FLUID_SLOT_MAX_VOLUMES
    upgrade_slots = 0
    allow_upgraders = frozenset()
    structure_palette = definition.STRUCTURE_PALETTE
    allow_unconfigured_structure = True
    functional_block_ids = set(port_id for port_id, cls in PORTS)

    def __init__(self, dim, x, y, z, block_entity_data):
        self._processing_recipe = False
        saved = block_entity_data[definition.K_BATCH]
        self._paid_recipe = GasMetallurgicalFurnaceRecipe.Unmarshal(json.loads(saved)) if saved else None
        super(GasMetallurgicalFurnace, self).__init__(dim, x, y, z, block_entity_data)
        self.bdata[definition.K_TEMPLATE_READY] = self.structure_palette is not None
        if self._paid_recipe is None:
            self.recheck_recipe()
        else:
            self.bdata[definition.K_RECIPE_ID] = self._paid_recipe.recipe_id
        self._init_ios()
        self._last_work_status = None
        self._update_work_status()

    def _update_work_status(self, flush=True):
        if not flush:
            return
        # 选中配方、解除停机都不等于已经加工；由实际推进进度的 tick 点亮。
        active = (self._processing_recipe and self._paid_recipe is not None
                  and self.ticks_left > 0 and self.StructureFinished() and self.IsActive())
        self._processing_recipe = active
        if active != self._last_work_status:
            block_state_comp = CF.CreateBlockState(LEVEL_ID)
            block_states = block_state_comp.GetBlockStates(self.xyz, self.dim)
            if block_states is not None:
                block_states["skybluetech:active"] = active
                block_state_comp.SetBlockStates(self.xyz, block_states, self.dim)
            self._last_work_status = active
            self.handler.CallOnWorkStatusUpdatedHandlers()

    def _base_speed_control_set_deactive_flag(self, flag, flush=True):
        if self._paid_recipe is None:
            super(GasMetallurgicalFurnace, self)._base_speed_control_set_deactive_flag(flag, flush)

    @accepts_slot_reads
    def get_recipe(self, slot_reads=None):
        if self._paid_recipe is not None:
            return 0, self._paid_recipe
        return Processor.get_recipe(self, slot_reads=slot_reads)

    def recheck_recipe(self):
        if self._paid_recipe is not None or self._applying_recipe:
            return
        _, recipe = self.get_recipe()
        self.current_recipe = recipe
        self.bdata[definition.K_RECIPE_ID] = recipe.recipe_id if recipe else ""
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE, recipe is None)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        self._output_dirty = True
        if recipe is not None:
            self.SetProcessTicks(recipe.tick_duration)
            self.ResetProgress()
            self.SetPower(recipe.tick_cost(0))
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)

    def _processor_on_ticking(self):
        # 这里只刷新接口实例的生命周期，不轮询或搬运接口库存。
        self._io_refresh_ticks += 1
        if self._io_refresh_ticks >= 20:
            self._io_refresh_ticks = 0
            self._refresh_io_bindings()
        recipe = self.current_recipe
        if recipe is None or not self.StructureFinished():
            self._processing_recipe = False
            self._update_work_status()
            return
        if self._output_dirty:
            self._check_output()
        elapsed = recipe.tick_duration - int(self.ticks_left) if self._paid_recipe else 0
        self.SetPower(recipe.tick_cost(elapsed) if elapsed < recipe.tick_duration else 0)
        if not self.PowerEnough() or not self.IsActive():
            self._processing_recipe = False
            self._update_work_status()
            return
        if self._paid_recipe is None and not self._begin_batch():
            self._processing_recipe = False
            self._update_work_status()
            return
        if self.ticks_left > 0:
            self.ProcessOnce()
            self._processing_recipe = True
        if self.ticks_left <= 0:
            self.run_once()
        self._update_work_status()
        self.CallSync()

    def _begin_batch(self):
        reads = SlotReads(self)
        _, recipe = reads.call(self.get_recipe)
        if recipe is None or not reads.call(self.can_output, recipe):
            self.recheck_recipe()
            return False
        if not recipe.equals(self.current_recipe):
            self.recheck_recipe()
            return False
        self._paid_recipe = recipe
        if not reads.call(self._apply_recipe, recipe, consume_inputs=True, produce_outputs=False):
            self._paid_recipe = None
            self.recheck_recipe()
            return False
        # 配方快照不依赖表中下标，配方表重排也能恢复已经投料的批次。
        self.bdata[definition.K_BATCH] = json.dumps(recipe.Marshal(), ensure_ascii=True)
        self.current_recipe = recipe
        self.SetProcessTicks(recipe.tick_duration)
        self.ticks_left = recipe.tick_duration
        self.bdata[definition.K_RECIPE_ID] = recipe.recipe_id
        self.transmit_materials()
        return True

    def ProcessOnce(self):
        self.ReducePower(bypass_upgraders=True)
        self.ticks_left -= 1
        return self.ticks_left <= 0

    def run_once(self):
        recipe = self._paid_recipe
        if recipe is None:
            return False
        if not self._apply_recipe(recipe, consume_inputs=False, produce_outputs=True):
            self._output_dirty = True
            return False
        self.bdata[definition.K_BATCH] = None
        self._paid_recipe = None
        self.recheck_recipe()
        self.transmit_materials()
        return True
