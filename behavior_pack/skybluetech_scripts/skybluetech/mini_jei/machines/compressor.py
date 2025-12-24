# coding=utf-8
#
from ...define.id_enum import machinery
from .recipe_cls import CategoryType, MachineRecipe, Input, Output


class CompressorRecipe(MachineRecipe):
    recipe_icon_id = machinery.COMPRESSOR
    render_ui_def_name = "RecipeCheckerUI.compressor_recipes"

    def __init__(self, inputs, outputs, power_cost, tick_duration):
        # type: (dict[int, Input], dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: inputs},
            {CategoryType.ITEM: outputs},
            power_cost,
            tick_duration,
        )

def gen_preset_recipe(
    power_cost, # type: int
    tick_duration, # type: int
):
    def generate_recipe(
        input, # type: str
        output, # type: str
    ):
        return CompressorRecipe(
            {0: Input(input)}, {1: Output(output)}, power_cost, tick_duration
        )
    return generate_recipe

def gen_preset_tagged_recipe(
    power_cost, # type: int
    tick_duration, # type: int
):
    def generate_recipe(
        input, # type: str
        output, # type: str
    ):
        return CompressorRecipe(
            {0: Input(input, is_tag=True)}, {1: Output(output)}, power_cost, tick_duration
        )
    return generate_recipe
