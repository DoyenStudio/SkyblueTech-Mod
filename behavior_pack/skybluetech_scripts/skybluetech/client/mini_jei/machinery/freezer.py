# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.freezer import (
    FreezerRecipe,
)
from .define import MachineRecipeRenderer


class FreezerRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = machinery.FREEZER
    render_ui_def_name = "RecipeCheckerLib.freezer_recipes"

    def __init__(self, recipe):
        # type: (FreezerRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipeRenderer.RenderInit(self, panel)
        panel["fake_btn/item_renderer"].asItemRenderer().SetUiItem(
            Item(self.recipe.output_item)
        )


FreezerRecipe.SetRenderer(FreezerRecipeRenderer)
