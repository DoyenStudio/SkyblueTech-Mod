# coding=utf-8

from ...common.define import flags
from ...common.define.id_enum import Machinery
from ...common.machinery_def.distillation_chamber import (
    CHAMBER_HEAT_CAPACITY,
    INPUT_MAX_VOLUME,
    K_OUTPUT_RATE,
    OUTPUT_MAX_VOLUME,
    DistillationChamberRecipe,
)
from ...common.machinery_def.distillation_chamber import (
    recipes as Recipes,
)
from .basic import (
    GUIControl,
    HeatCtrl,
    MultiFluidContainer,
)
from .core import RegisterMachine
from .basic.multi_fluid_container import FluidSlotServer

TICKS_PER_SECOND = 20

recipes_collection = {}  # type: dict[str, list[DistillationChamberRecipe]]
for recipe in Recipes:
    recipes_collection.setdefault(recipe.collection_name, []).append(recipe)

# 没有产出的原因 (互斥): 缺少输入 / 温度不在任何配方范围内 / 产出槽放不下
IDLE_FLAGS = (
    flags.DEACTIVE_FLAG_NO_INPUT,
    flags.DEACTIVE_FLAG_NO_RECIPE,
    flags.DEACTIVE_FLAG_FLUID_FULL,
)


@RegisterMachine
class DistillationChamber(GUIControl, MultiFluidContainer, HeatCtrl):
    block_name = Machinery.DISTILLATION_CHAMBER
    is_non_energy_machine = True
    heat_capacity = CHAMBER_HEAT_CAPACITY
    # 本机热容远大于默认值, 产油扣热才不会把仓温踹穿, 见 CHAMBER_HEAT_CAPACITY
    fluid_io_fix_mode = 0
    fluid_input_slots = (0,)
    fluid_output_slots = (1,)
    fluid_slot_max_volumes = {0: INPUT_MAX_VOLUME, 1: OUTPUT_MAX_VOLUME}

    def __init__(self, dim, x, y, z, block_entity_data):
        super(DistillationChamber, self).__init__(dim, x, y, z, block_entity_data)
        self.locked_recipe_idx = None
        self.output_rate = 0
        self._produce_accum = 0.0
        self._tick_counter = 0
        self.handler.SubscribeOnTicking(self._distillation_chamber_on_ticking)
        self.handler.SubscribeOnSync(self._distillation_chamber_on_sync)
        self.CallSync()


    def _distillation_chamber_on_ticking(self):
        self.set_idle_reason(self.work_once())
        self._tick_counter += 1
        if self._tick_counter >= TICKS_PER_SECOND:
            self.output_rate = self._produce_accum
            self._produce_accum = 0.0
            self._tick_counter = 0
            self.CallSync()

    def _distillation_chamber_on_sync(self):
        # type: () -> None
        self.bdata[K_OUTPUT_RATE] = self.output_rate

    def IsValidFluidInput(self, slot, fluid_id):
        # type: (int, str) -> bool
        results = (
            MultiFluidContainer.IsValidFluidInput(self, slot, fluid_id),
            self._distillation_chamber_is_valid_fluid_input(slot, fluid_id),
        )
        return all(results)

    def _distillation_chamber_is_valid_fluid_input(self, slot, fluid_id):
        # type: (int, str) -> bool
        return fluid_id in recipes_collection

    def set_idle_reason(self, reason):
        # type: (int) -> None
        "本 tick 没有产出的原因 (0 = 正常产出); 只在原因变化时改停机标志, 状态灯与提示圈随之更新。"
        for flag in IDLE_FLAGS:
            self.UpdateDeactiveFlag(flag, flag == reason)

    def work_once(self):
        # type: () -> int
        "尝试蒸馏一次, 返回没能产出的原因 (IDLE_FLAGS 之一, 0 = 已产出)。"
        in_fluid = self.fluids[0]
        out_fluid = self.fluids[1]
        input_fluid_id = in_fluid.fluid_id
        if input_fluid_id is None:
            return flags.DEACTIVE_FLAG_NO_INPUT
        rcps = recipes_collection.get(input_fluid_id)
        if rcps is None:
            return flags.DEACTIVE_FLAG_NO_RECIPE
        if self.locked_recipe_idx is None:
            for idx, rcp in enumerate(rcps):
                if (
                    self.kelvin > rcp.min_temperature
                    and self.kelvin < rcp.max_temperature
                ):
                    reason = self.work_with_recipe(rcp, in_fluid, out_fluid)
                    self.locked_recipe_idx = idx
                    return reason
            return flags.DEACTIVE_FLAG_NO_RECIPE
        rcp = rcps[self.locked_recipe_idx]
        if self.kelvin > rcp.min_temperature:
            return self.work_with_recipe(rcp, in_fluid, out_fluid)
        return flags.DEACTIVE_FLAG_NO_RECIPE

    def work_with_recipe(self, rcp, in_fluid, out_fluid):
        # type: (DistillationChamberRecipe, FluidSlotServer, FluidSlotServer) -> int
        T = self.kelvin
        T_min = rcp.min_temperature
        T_fit = rcp.fit_temperature
        T_max = rcp.max_temperature
        if T <= T_min:
            return flags.DEACTIVE_FLAG_NO_RECIPE
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
        if in_fluid.volume < consume:
            return flags.DEACTIVE_FLAG_NO_INPUT
        if out_fluid.max_volume - out_fluid.volume < produce:
            return flags.DEACTIVE_FLAG_FLUID_FULL
        in_fluid.volume -= consume
        self._produce_accum += produce
        self.OutputFluid(rcp.produce_matter, produce, 1, True)
        self.heat_value -= produce * rcp.heat_per_produce
        if in_fluid.volume <= 0:
            in_fluid.fluid_id = None
        return 0
