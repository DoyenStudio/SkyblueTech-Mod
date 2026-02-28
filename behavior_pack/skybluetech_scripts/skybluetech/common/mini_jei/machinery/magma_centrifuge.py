# coding=utf-8
#
from ....common.define.id_enum import machinery
from .recipe_cls import CategoryType, MachineRecipe, Input, Output


class MagmaCentrifugeRecipe(MachineRecipe):
    recipe_icon_id = machinery.MAGMA_CENTRIFUGE
    render_ui_def_name = "RecipeCheckerUI.magma_centrifuge_recipes"

    def __init__(self, input_fluid, input_volume, outputs, power_cost, tick_duration):
        # type: (str, float, dict[int, Output], int, int) -> None
        MachineRecipe.__init__(
            self,
            {CategoryType.FLUID: {0: Input(input_fluid, input_volume)}},
            {CategoryType.FLUID: outputs},
            power_cost,
            tick_duration,
        )
