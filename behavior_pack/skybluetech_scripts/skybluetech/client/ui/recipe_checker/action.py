# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UButton
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ....common.mini_jei import RecipeBase
from .recipe_checker_ui import RecipeCheckerUI


def PushRecipeCheckerUI(recipes):
    # type: (list[RecipeBase]) -> RecipeCheckerUI
    if len(recipes) == 0:
        raise ValueError("Can't push an empty recipe list")
    recipe_ins = recipes[0]
    uiNode = RecipeCheckerUI.PushUI({
        "recipes": [
            (
                recipe_ins.recipe_icon_id,
                recipe_ins.minijei_title or GetItemHoverName(recipe_ins.recipe_icon_id),
                recipes,
            )
        ]
    })
    return uiNode


def AsRecipeCheckerBtn(
    ctrl,  # type: UButton
    recipes,  # type: list[RecipeBase]
):
    def cb(params):
        PushRecipeCheckerUI(recipes)

    ctrl.SetCallback(cb)
