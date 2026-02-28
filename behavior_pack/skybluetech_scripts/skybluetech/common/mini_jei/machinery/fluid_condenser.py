# coding=utf-8
#
from ....common.define.id_enum import machinery
from .recipe_cls import CategoryType, MachineRecipe, Input, Output

MC_METAL = {"copper", "iron", "gold"}


class FluidCondenserRecipe(MachineRecipe):
    recipe_icon_id = machinery.FLUID_CONDENSER
    render_ui_def_name = "RecipeCheckerUI.fluid_condenser_recipes"

    def __init__(
        self,
        input_fluid,  # type: str
        input_fluid_volume,  # type: float
        output_item,  # type: str
        output_item_count,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_fluid_volume)}},
            {CategoryType.ITEM: {0: Output(output_item, output_item_count)}},
            power_cost,
            tick_duration,
        )


def recipe_molten2ingot(metal_id, power_cost=80, tick_duration=180):
    # type: (str, int, int) -> FluidCondenserRecipe
    return FluidCondenserRecipe(
        "skybluetech:molten_" + metal_id,
        144,
        ("minecraft:" if metal_id in MC_METAL else "skybluetech:")
        + metal_id
        + "_ingot",
        1,
        power_cost,
        tick_duration,
    )
