# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import DISTILLATION_CHAMBER as MACHINE_ID
from ...common.machinery_def.distillation_chamber import (
    recipes as Recipes,
    DistillationChamberRecipe,
)
from .basic import (
    BaseMachine,
    HeatCtrl,
    MultiFluidContainer,
    GUIControl,
    RegisterMachine,
)
from ...common.machinery_def.distillation_chamber import (
    K_OUTPUT_RATE,
    INPUT_MAX_VOLUME,
    OUTPUT_MAX_VOLUME,
)
from .basic.multi_fluid_container import FluidSlotServer

TICKS_PER_SECOND = 20

recipes_collection = {}  # type: dict[str, list[DistillationChamberRecipe]]
for recipe in Recipes:
    recipes_collection.setdefault(recipe.collection_name, []).append(recipe)


@RegisterMachine
class DistillationChamber(HeatCtrl, MultiFluidContainer, GUIControl):
    block_name = MACHINE_ID
    is_non_energy_machine = True
    fluid_io_fix_mode = 0
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_slot_max_volumes = (INPUT_MAX_VOLUME, OUTPUT_MAX_VOLUME)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.locked_recipe_idx = None
        self.output_rate = 0
        self._produce_accum = 0.0
        self._tick_counter = 0

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        self.work_once()
        self._tick_counter += 1
        if self._tick_counter >= TICKS_PER_SECOND:
            self.output_rate = self._produce_accum
            self._produce_accum = 0.0
            self._tick_counter = 0
            self.CallSync()

    def OnSync(self):
        # type: () -> None
        self.bdata[K_OUTPUT_RATE] = self.output_rate

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id in recipes_collection

    def work_once(self):
        in_fluid = self.fluids[0]
        out_fluid = self.fluids[1]
        input_fluid_id = in_fluid.fluid_id
        if input_fluid_id is None:
            return
        rcps = recipes_collection.get(input_fluid_id)
        if rcps is None:
            return
        if self.locked_recipe_idx is None:
            for idx, rcp in enumerate(rcps):
                if (
                    self.kelvin > rcp.min_temperature
                    and self.kelvin < rcp.max_temperature
                ):
                    self.work_with_recipe(rcp, in_fluid, out_fluid)
                    self.locked_recipe_idx = idx
                    break
        else:
            rcp = rcps[self.locked_recipe_idx]
            if self.kelvin > rcp.min_temperature:
                self.work_with_recipe(rcp, in_fluid, out_fluid)

    def work_with_recipe(self, rcp, in_fluid, out_fluid):
        # type: (DistillationChamberRecipe, FluidSlotServer, FluidSlotServer) -> None
        T = self.kelvin
        T_min = rcp.min_temperature
        T_fit = rcp.fit_temperature
        T_max = rcp.max_temperature
        if T <= T_min:
            return
        if T <= T_fit:
            produce_rate = consume_rate = float(T - T_min) / (T_fit - T_min)
        elif T <= T_max:
            produce_rate = 1.0
            consume_rate = float(T - T_min) / (T_fit - T_min)
        else:
            produce_rate = 1.0
            consume_rate = float(T_max - T_min) / (T_fit - T_min)
        consume = rcp.consume * consume_rate
        produce = rcp.produce * produce_rate
        if in_fluid.volume >= consume:
            if out_fluid.max_volume - out_fluid.volume >= produce:
                in_fluid.volume -= consume
                self._produce_accum += produce
                self.OutputFluid(rcp.produce_matter, produce, 1, True)
                self.heat_value -= produce
                if in_fluid.volume <= 0:
                    in_fluid.fluid_id = None
