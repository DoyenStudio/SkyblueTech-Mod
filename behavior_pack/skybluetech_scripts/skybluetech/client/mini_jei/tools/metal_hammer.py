# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import METAL_HAMMER
from skybluetech_scripts.skybluetech.common.mini_jei.tools.metal_hammer import (
    MetalHammerRecipe,
)
from ...ui.recipe_checker.render_utils import ItemDisplayer
from ...ui.recipe_checker.render_utils_advanced import InputDisplayer
from ..core import RecipeRenderer


class MetalHammerRecipeRenderer(RecipeRenderer):
    recipe_icon_id = METAL_HAMMER
    render_ui_def_name = "RecipeCheckerLib.metal_hammer_recipes"
    minijei_title = "金属锤锤锭获得"

    def __init__(self, recipe):
        # type: (MetalHammerRecipe) -> None
        RecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel_ctrl):
        # type: (UBaseCtrl) -> None
        self.input_renderer = InputDisplayer(panel_ctrl["slot0"], self.recipe.hammer_in)
        self.output_renderer = ItemDisplayer(
            panel_ctrl["slot1"], Item(self.recipe.hammer_out)
        )


MetalHammerRecipe.SetRenderer(MetalHammerRecipeRenderer)
