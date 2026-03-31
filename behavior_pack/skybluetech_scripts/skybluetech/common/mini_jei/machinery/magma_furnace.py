# coding=utf-8
#
from ....common.define.id_enum import machinery
from .define import CategoryType, MachineRecipe, Input, Output


def sec(second):
    # type: (float) -> int
    return int(second * 20)


class MagmaFurnaceRecipe(MachineRecipe):
    recipe_icon_id = machinery.MAGMA_FURNACE
    render_ui_def_name = "RecipeCheckerLib.magma_furnace_recipes"

    def __init__(
        self, input_id, is_tag, output_fluid, output_volume, power_cost, tick_duration
    ):
        # type: (str, bool, str, float, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_id, is_tag=is_tag)}},
            {CategoryType.FLUID: {0: Output(output_fluid, output_volume)}},
            power_cost,
            tick_duration,
        )
