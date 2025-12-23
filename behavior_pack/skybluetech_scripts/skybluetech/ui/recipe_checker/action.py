# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UButton
from ...mini_jei.core.define import RecipeBase
from .recipe_checker_ui import RecipeCheckerUI

def PushRecipeCheckerUI(icon_item_name, recipes):
    # type: (str, list[RecipeBase]) -> RecipeCheckerUI
    uiNode = RecipeCheckerUI.PushUI()
    uiNode.PushRecipes({icon_item_name: recipes})
    return uiNode

def AsRecipeCheckerBtn(
    ctrl, # type: UButton
    icon_item_name, # type: str
    recipes, # type: list[RecipeBase]
):
    def cb(params):
        PushRecipeCheckerUI(icon_item_name, recipes)
    ctrl.SetCallback(cb)

