# coding=utf-8
from ...common.define import flags
from ...common.define.id_enum import Acid, Gas, LargeReactionPool as Pool
from ...common.machinery_def import large_reaction_pool as definition
from ...common.mini_jei.machinery.large_reaction_pool import LargeReactionPoolRecipe
from .basic import HeatCtrl
from .basic.multiblock_batch_processor import MultiblockBatchProcessor
from .core import RegisterMachine
from .interfaces import (
    EnergyInputInterface, FluidInputInterface, FluidOutputInterface, HeatInputInterface,
    ItemInputInterface, ItemOutputInterface,
)

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
class LargeReactionPool(MultiblockBatchProcessor, HeatCtrl):
    block_name = Pool.CONTROLLER
    structure_palette = definition.STRUCTURE_PALETTE
    functional_block_ids = frozenset([p for p, _ in PORTS] + [Pool.WINDOW])
    ports = PORTS
    fluid_inputs_by_port = FLUID_INPUTS
    fluid_outputs_by_port = FLUID_OUTPUTS
    item_input_port = Pool.IO_ITEM_INPUT
    item_output_port = Pool.IO_ITEM_OUTPUT
    batch_key = definition.K_BATCH
    recipe_id_key = definition.K_RECIPE_ID
    batch_recipe_type = LargeReactionPoolRecipe
    work_units_per_tick = UNITS_PER_TICK
    work_key = K_WORK
    refresh_ports_on_sync = False
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
        self._surface = object()
        super(LargeReactionPool, self).__init__(dim, x, y, z, block_entity_data)

    def recheck_recipe(self):
        if self._batch is None and not self._applying_recipe:
            self.UnsetDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK)
        super(LargeReactionPool, self).recheck_recipe()

    def _step_units(self, recipe):
        if not recipe.heat_cost:
            return UNITS_PER_TICK
        if self.kelvin < recipe.min_temperature:
            return 0
        factor = (self.kelvin - recipe.min_temperature) / float(recipe.fit_temperature - recipe.min_temperature)
        return max(1, min(UNITS_PER_TICK, int(UNITS_PER_TICK * factor)))

    def _batch_step_and_cost(self, recipe, remaining):
        step = min(remaining, self._step_units(recipe))
        self.UpdateDeactiveFlag(flags.DEACTIVE_FLAG_HEAT_LACK, step == 0 and remaining > 0)
        # 累计向上取整的差值保证整批电费与配方表相同。
        charge = ((self._work + step) * recipe.power_cost + UNITS_PER_TICK - 1) // UNITS_PER_TICK
        charge -= (self._work * recipe.power_cost + UNITS_PER_TICK - 1) // UNITS_PER_TICK
        return step, charge

    def _advance_work(self, recipe, step):
        if recipe.heat_cost:
            self.heat_value -= recipe.heat_cost * step / float(recipe.tick_duration * UNITS_PER_TICK)
        super(LargeReactionPool, self)._advance_work(recipe, step)

    def _refresh_io_bindings(self):
        super(LargeReactionPool, self)._refresh_io_bindings()
        # 有效结构之间直接替换窗或衬板时，接口实例可能完全相同。
        self._update_surface()

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
