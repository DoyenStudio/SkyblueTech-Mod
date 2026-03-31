# coding=utf-8
#
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


class MetalPressRecipe(MachineRecipe):
    recipe_icon_id = machinery.METAL_PRESS
    render_ui_def_name = "RecipeCheckerLib.metal_press_recipes"

    def __init__(
        self,
        input_fluid,  # type: str
        input_volume,  # type: float
        input_item,  # type: str
        input_count,  # type: int
        output_item,  # type: str
        output_count,  # type: int
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {
                CategoryType.FLUID: {0: Input(input_fluid, input_volume)},
                CategoryType.ITEM: {0: Input(input_item, input_count)},
            },
            {CategoryType.ITEM: {1: Output(output_item, output_count)}},
            power_cost,
            tick_duration,
        )
