# coding=utf-8
#
from .define import CategoryType, MachineRecipe, Input, Output

MACHINE_ID = "skybluetech:freezer"


class FreezerRecipe(MachineRecipe):
    recipe_icon_id = MACHINE_ID
    render_ui_def_name = "RecipeCheckerUI.freezer_recipes"

    def __init__(
        self,
        index, # type: int
        input_fluid, # type: str
        input_volume, # type: float
        output_item, # type: str
        output_count, # type: int
        power_cost, # type: int
        tick_duration, # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.ITEM: {0: Output(output_item, output_count)}},
            power_cost,
            tick_duration,
        )
        self.index = index
