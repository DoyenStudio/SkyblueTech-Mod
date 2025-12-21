# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UButton
from ...define.machine_config.define import MachineRecipe
from .recipe_checker_ui import RecipeCheckerUI

def PushRecipeCheckerUI(icon_item_name, recipes):
    # type: (str, list[MachineRecipe]) -> RecipeCheckerUI
    uiNode = RecipeCheckerUI.PushUI()
    uiNode.SetRecipes({icon_item_name: recipes})
    return uiNode

def AsRecipeCheckerBtn(
    ctrl, # type: UButton
    icon_item_name, # type: str
    recipes, # type: list[MachineRecipe]
):
    def cb(params):
        PushRecipeCheckerUI(icon_item_name, recipes)
    ctrl.SetCallback(cb)

