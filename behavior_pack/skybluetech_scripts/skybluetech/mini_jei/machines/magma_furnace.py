# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

def sec(second):
    # type: (float) -> int
    return int(second * 20)

MACHINE_ID = "skybluetech:magma_furnace"
raw2motten_vol = 432
ingot2motten_vol = 144



class MagmaFurnaceRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.magma_furnace_recipes"

    def __init__(self, input_id, is_tag, output_fluid, output_volume, power_cost, tick_duration):
        # type: (str, bool, str, float, int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_id, is_tag=is_tag)}},
            {CategoryType.FLUID: {0: Output(output_fluid, output_volume)}},
            power_cost,
            tick_duration,
        )

