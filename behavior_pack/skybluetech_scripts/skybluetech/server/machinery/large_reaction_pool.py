# coding=utf-8
import json

from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from ...common.define import flags
from ...common.define.id_enum import Acid, Gas, LargeReactionPool as Pool
from ...common.machinery_def import large_reaction_pool as definition
from ...common.mini_jei.machinery.large_reaction_pool import LargeReactionPoolRecipe
from .basic import HeatCtrl, MultiBlockStructure, MultiFluidContainer, Processor
from .basic.slot_reads import SlotReads, accepts_slot_reads
from .core import RegisterMachine
from .interfaces import (
    EnergyInputInterface, FluidInputInterface, FluidOutputInterface, HeatInputInterface,
    ItemInputInterface, ItemOutputInterface,
)
from .multiblock_processing_ports import MultiblockProcessingPorts

FLUID_INPUTS = ((Pool.IO_FLUID_INPUT_1, 0), (Pool.IO_FLUID_INPUT_2, 1), (Pool.IO_FLUID_INPUT_3, 3))
FLUID_OUTPUTS = ((Pool.IO_FLUID_OUTPUT_1, 2), (Pool.IO_FLUID_OUTPUT_2, 4))
PORTS = (
    (Pool.IO_ENERGY_INPUT, EnergyInputInterface), (Pool.IO_HEAT_INPUT, HeatInputInterface),
    (Pool.IO_ITEM_INPUT, ItemInputInterface), (Pool.IO_ITEM_OUTPUT, ItemOutputInterface),
) + tuple((p, FluidInputInterface) for p, _ in FLUID_INPUTS) + tuple((p, FluidOutputInterface) for p, _ in FLUID_OUTPUTS)
for port_id, interface in PORTS:
    interface.AddExtraMachineId(port_id)

# 整数千分之一 tick 是持久化进度，慢速与读档都用累计进度差结算。
UNITS_PER_TICK = 1000
K_WORK = "st:reaction_pool_work"


@RegisterMachine
class LargeReactionPool(MultiblockProcessingPorts, Processor, MultiFluidContainer, MultiBlockStructure, HeatCtrl):
    block_name = Pool.CONTROLLER
    structure_palette = definition.STRUCTURE_PALETTE
    functional_block_ids = frozenset([p for p, _ in PORTS] + [Pool.WINDOW])
    ports = PORTS
    fluid_inputs_by_port = FLUID_INPUTS
    fluid_outputs_by_port = FLUID_OUTPUTS
    item_input_port = Pool.IO_ITEM_INPUT
    item_output_port = Pool.IO_ITEM_OUTPUT
    recipes = definition.recipes
    process_item = process_fluid = True
    item_input_slots = (0,)
    item_output_slots = (1,)
    item_input_slots_by_face = {}
    item_output_slots_by_face = {}
    fluid_input_slots = definition.FLUID_INPUT_SLOTS
    fluid_output_slots = definition.FLUID_OUTPUT_SLOTS
    fluid_slot_max_volumes = definition.FLUID_SLOT_MAX_VOLUMES
    store_rf_max = definition.STORE_RF_MAX
    heat_capacity = 50.0
    heat_input_faces = heat_output_faces = ()
    energy_io_mode = (2,) * 6
    upgrade_slots = 0
    allow_upgraders = frozenset()

    def __init__(self, dim, x, y, z, block_entity_data):
        saved = block_entity_data[definition.K_BATCH]
        self._batch = LargeReactionPoolRecipe.Unmarshal(json.loads(saved)) if saved else None
        self._work = int(block_entity_data[K_WORK] or 0) if saved else 0
        self._advancing = False
        self._surface = object()
        super(LargeReactionPool, self).__init__(dim, x, y, z, block_entity_data)
        if self._batch is not None:
            self.ticks_left = self._batch.tick_duration - self._work / float(UNITS_PER_TICK)
            self.bdata[definition.K_RECIPE_ID] = self._batch.recipe_id
        else:
            self.recheck_recipe()
        self._init_ios(refresh_on_sync=False)
        self._last_work_status = None
        self._update_work_status()
        self._update_surface()

    @accepts_slot_reads
    def get_recipe(self, slot_reads=None):
        if self._batch:
            return 0, self._batch
        return Processor.get_recipe(self, slot_reads=slot_reads)

    def recheck_recipe(self):
        if self._batch or self._applying_recipe:
            return
        _, recipe = self.get_recipe()
        self.current_recipe = recipe
        self._output_dirty = True
        self.bdata[definition.K_RECIPE_ID] = recipe.recipe_id if recipe else ""
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_NO_RECIPE, recipe is None)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_NO_INPUT)
        self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK)
        if recipe:
            self.SetProcessTicks(recipe.tick_duration)
            self.SetPower(recipe.power_cost)
        else:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_OUTPUT_FULL)
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_POWER_LACK)
        self.ResetProgress()

    def _base_speed_control_set_deactive_flag(self, flag, flush=True):
        if self._batch is None:
            super(LargeReactionPool, self)._base_speed_control_set_deactive_flag(flag, flush)

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
        self._work = self.bdata[K_WORK] = 0
        self.bdata[definition.K_BATCH] = json.dumps(recipe.Marshal(), ensure_ascii=True)
        self.transmit_materials()
        return True

    def _step_units(self, recipe):
        if not recipe.heat_cost:
            return UNITS_PER_TICK
        if self.kelvin < recipe.min_temperature:
            return 0
        factor = (self.kelvin - recipe.min_temperature) / float(recipe.fit_temperature - recipe.min_temperature)
        return max(1, min(UNITS_PER_TICK, int(UNITS_PER_TICK * factor)))

    def _processor_on_ticking(self):
        self._io_refresh_ticks += 1
        if self._io_refresh_ticks >= 20:
            self._io_refresh_ticks = 0
            self._refresh_io_bindings()
            # 有效结构之间直接替换窗或衬板时，接口实例可能完全相同。
            self._update_surface()
        self._advancing = False
        recipe = self.current_recipe
        if recipe is not None and self.StructureFinished():
            self._advance_batch(recipe)
        self._update_work_status()

    def _advance_batch(self, recipe):
        if self._output_dirty:
            self._check_output()
        total = recipe.tick_duration * UNITS_PER_TICK
        step = min(total - self._work, self._step_units(recipe))
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK, step == 0 and self._work < total)
        # 累计向上取整的差值保证整批电费与配方表相同。
        charge = ((self._work + step) * recipe.power_cost + UNITS_PER_TICK - 1) // UNITS_PER_TICK
        charge -= (self._work * recipe.power_cost + UNITS_PER_TICK - 1) // UNITS_PER_TICK
        self.SetPower(charge)
        if not self.PowerEnough() or not self.IsActive():
            return
        if self._batch is None and not self._begin_batch(recipe):
            return
        if step:
            self.ReducePower(charge, bypass_upgraders=True)
            if recipe.heat_cost:
                self.heat_value -= recipe.heat_cost * step / float(total)
            self._work += step
            self.bdata[K_WORK] = self._work
            self.ticks_left = (total - self._work) / float(UNITS_PER_TICK)
            self._advancing = True
        if self._work == total:
            if not self._apply_recipe(recipe, consume_inputs=False, produce_outputs=True):
                self._output_dirty = True
                return
            self._batch = self.bdata[definition.K_BATCH] = None
            self._work = self.bdata[K_WORK] = 0
            self.recheck_recipe()
            self.transmit_materials()

    def _on_structure_changed(self, ok):
        super(LargeReactionPool, self)._on_structure_changed(ok)
        self._update_surface()

    def transmit_materials(self):
        if self._io_busy or self._applying_recipe:
            return
        super(LargeReactionPool, self).transmit_materials()
        self._update_surface()

    def _channel_surface(self, port, slot):
        tanks = [self.fluids[slot]] + [machine.fluids[0] for machine in self._live_ports(port)]
        volumes = {}
        for tank in tanks:
            fid = tank.fluid_id
            if fid and fid not in Gas.all_sub() and fid != Acid.HYDROGEN_CHLORIDE:
                volumes[fid] = volumes.get(fid, 0.0) + tank.volume
        if not volumes:
            return None
        fid = min(volumes, key=lambda key: (-volumes[key], key))
        return fid, volumes[fid], sum(tank.max_volume for tank in tanks)

    def _update_surface(self):
        surface = None
        if self.StructureFinished() and self.GetFunctionalBlockPoses().get(Pool.WINDOW):
            liquid = self._channel_surface(*FLUID_OUTPUTS[0])
            if not liquid:
                for port, slot in FLUID_INPUTS:
                    candidate = self._channel_surface(port, slot)
                    if candidate and (not liquid or candidate[1] > liquid[1]):
                        liquid = candidate
            if liquid:
                x, y, z = min(self.area.rotated_palette.air_poses, key=lambda pos: pos[1])
                fid, volume, capacity = liquid
                surface = (fid, volume / float(capacity), x + 0.5, float(y), z + 0.5)
        if surface != self._surface:
            self._surface = surface
            self.bdata[definition.K_SURFACE] = (
                {"id": surface[0], "ratio": surface[1], "origin": list(surface[2:])} if surface else None
            )
