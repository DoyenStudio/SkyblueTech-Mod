# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:macerator"


class MaceratorRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.macerator_recipes"

    def __init__(self, input, output_id, output_count, power_cost, tick_duration):
        # type: (Input, str, int, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: input}},
            {CategoryType.ITEM: {1: Output(output_id, output_count)}},
            power_cost,
            tick_duration,
        )


def gen_preset_recipe(
    power_cost, # type: int
    tick_duration, # type: int
):
    def generate_recipe(
        input, # type: str
        input_count, # type: int
        output, # type: str
        output_count, # type: int
    ):
        return MaceratorRecipe(
            Input(input, input_count),
            output, output_count,
            power_cost, tick_duration
        )
    return generate_recipe

def gen_tagged_preset_recipe(
    power_cost, # type: int
    tick_duration, # type: int
):
    def generate_recipe(
        input, # type: str
        input_count, # type: int
        output, # type: str
        output_count, # type: int
    ):
        return MaceratorRecipe(
            Input(input, input_count, is_tag=True),
            output, output_count,
            power_cost, tick_duration
        )
    return generate_recipe

