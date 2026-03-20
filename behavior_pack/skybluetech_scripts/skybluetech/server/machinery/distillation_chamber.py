# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.super_executor import SuperExecutorMeta
from ...common.define.id_enum.machinery import DISTILLATION_CHAMBER as MACHINE_ID
from ...common.machinery_def.distillation_chamber import (
    recipes as Recipes,
    DistillatorChamberRecipe,
)
from ...common.ui_sync.machinery.distillation_chamber import DistillationChamberUISync
from .basic import (
    BaseMachine,
    HeatCtrl,
    MultiFluidContainer,
    GUIControl,
    RegisterMachine,
)
from .basic.multi_fluid_container import FluidSlot

recipes_collection = {}  # type: dict[str, list[DistillatorChamberRecipe]]
for recipe in Recipes:
    recipes_collection.setdefault(recipe.collection_name, []).append(recipe)


@RegisterMachine
class DistillatorChamber(HeatCtrl, MultiFluidContainer, GUIControl):
    block_name = MACHINE_ID
    is_non_energy_machine = True
    fluid_io_fix_mode = 0
    fluid_input_slots = {0}
    fluid_output_slots = {1}
    fluid_slot_max_volumes = (1500, 1000)

    @SuperExecutorMeta.execute_super
    def __init__(self, dim, x, y, z, block_entity_data):
        self.sync = DistillationChamberUISync.NewServer(self).Activate()
        self.locked_recipe_idx = None
        self.output_rate = 0

    @SuperExecutorMeta.execute_super
    def OnUnload(self):
        pass

    @SuperExecutorMeta.execute_super
    def OnTicking(self):
        self.output_rate = 0
        self.work_once()
        self.CallSync()

    def OnSync(self):
        # type: () -> None
        self.sync.current_temperature = self.kelvin
        self.sync.output_rate = self.output_rate
        self.sync.lower_fluid_id = self.fluids[0].fluid_id
        self.sync.lower_fluid_volume = self.fluids[0].volume
        self.sync.lower_fluid_max_volume = self.fluids[0].max_volume
        self.sync.upper_fluid_id = self.fluids[1].fluid_id
        self.sync.upper_fluid_volume = self.fluids[1].volume
        self.sync.upper_fluid_max_volume = self.fluids[1].max_volume
        self.sync.MarkedAsChanged()

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id in recipes_collection

    def OnAddedFluid(self, slot, fluid_id, add_fluid_volume):
        # type: (int, str, float) -> None
        if slot == 0:
            cur_volume = self.fluids[0].volume
            prev_volume = cur_volume - add_fluid_volume
            self.InputFluidAndUpdateHeat(fluid_id, prev_volume, cur_volume)

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
            if self.kelvin > rcp.min_temperature and self.kelvin < rcp.max_temperature:
                self.work_with_recipe(rcp, in_fluid, out_fluid)

    def work_with_recipe(self, rcp, in_fluid, out_fluid):
        # type: (DistillatorChamberRecipe, FluidSlot, FluidSlot) -> None
        if self.kelvin < rcp.fit_temperature:
            consume_rate = produce_rate = float(rcp.fit_temperature - self.kelvin) / (
                rcp.fit_temperature - rcp.min_temperature
            )
        else:
            consume_rate = 1
            produce_rate = 1 - float(self.kelvin - rcp.fit_temperature) / (
                rcp.max_temperature - rcp.fit_temperature
            )
        consume = rcp.consume * consume_rate
        produce = rcp.produce * produce_rate
        if in_fluid.volume >= consume:
            # TODO: 即使剩余量不足单次产量也按比例进行产出
            if out_fluid.max_volume - out_fluid.volume >= produce:
                in_fluid.volume -= consume
                self.output_rate = produce_rate
                self.OutputFluid(rcp.produce_matter, produce, 1, True)
