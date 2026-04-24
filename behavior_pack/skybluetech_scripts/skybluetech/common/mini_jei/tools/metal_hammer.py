# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from ...define.id_enum import METAL_HAMMER
from ..core import CategoryType, Recipe, Input, Output


class MetalHammerRecipe(Recipe):
    recipe_icon_id = METAL_HAMMER
    render_ui_def_name = "RecipeCheckerLib.metal_hammer_recipes"
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
        from ....client.ui.recipe_checker.render_utils import ItemDisplayer
        from ....client.ui.recipe_checker.render_utils_advanced import InputDisplayer

        Recipe.RenderInit(self, panel_ctrl)
        self.input_renderer = InputDisplayer(panel_ctrl["slot0"], self.hammer_in)
        self.output_renderer = ItemDisplayer(panel_ctrl["slot1"], Item(self.hammer_out))

    def __hash__(self):
        return hash(self.hammer_in) ^ hash(self.hammer_out)

    def __eq__(self, other):
        if not isinstance(other, MetalHammerRecipe):
            return False
        return self.hammer_in == other.hammer_in and self.hammer_out == other.hammer_out
