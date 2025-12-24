# coding=utf-8
#
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from ...define.id_enum import machinery
from .recipe_cls import CategoryType, MachineRecipe, Input, Output


class FreezerRecipe(MachineRecipe):
    recipe_icon_id = machinery.FREEZER
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
        self.output_item = output_item

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipe.RenderInit(self, panel)
        panel["fake_btn/item_renderer"].asItemRenderer().SetUiItem(Item(self.output_item))
