# coding=utf-8
#
from .recipe_cls import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:alloy_furnace"


class AlloyFurnaceRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.alloy_furnace_recipes"

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
        inputs, # type: dict[int, Input]
        outputs, # type: dict[int, Output]
    ):
        return AlloyFurnaceRecipe(
            inputs, outputs, power_cost, tick_duration
        )
    return generate_recipe



