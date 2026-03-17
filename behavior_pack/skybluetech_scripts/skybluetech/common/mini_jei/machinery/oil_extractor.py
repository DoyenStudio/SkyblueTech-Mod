# coding=utf-8
#
from ....common.define.id_enum import machinery
from .recipe_cls import CategoryType, MachineRecipe, Input, Output


class OilExtractorRecipe(MachineRecipe):
    recipe_icon_id = machinery.OIL_EXTRACTOR
    render_ui_def_name = "RecipeCheckerLib.oil_extractor_recipes"

    def __init__(
        self,
        input_item,  # type: str
        output_fluid,  # type: str
        output_fluid_volume,  # type: float
        power_cost,  # type: int
        tick_duration,  # type: int
    ):
        MachineRecipe.__init__(
            self,
            {CategoryType.ITEM: {0: Input(input_item, 1)}},
            {CategoryType.FLUID: {0: Output(output_fluid, output_fluid_volume)}},
            power_cost,
            tick_duration,
        )
