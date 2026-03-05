# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from ...define.id_enum import METAL_HAMMER
from ..core import CategoryType, Recipe, Input, Output, InputDisplayer, ItemDisplayer


class MetalHammerRecipe(Recipe):
    recipe_icon_id = METAL_HAMMER
    render_ui_def_name = "RecipeCheckerUI.metal_hammer_recipes"
    minijei_title = "金属锤锤锭获得"

    def __init__(self, input, output_id):
        # type: (Input, str) -> None
        Recipe.__init__(
            self,
            {CategoryType.ITEM: {0: input}},
            {CategoryType.ITEM: {0: Output(output_id)}},
        )
        self.hammer_in = input
        self.hammer_out = output_id

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        self.input_renderer = InputDisplayer(panel_ctrl["slot0"], self.hammer_in)
        self.output_renderer = ItemDisplayer(panel_ctrl["slot1"], Item(self.hammer_out))
