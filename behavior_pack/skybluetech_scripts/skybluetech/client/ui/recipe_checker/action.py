# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UButton
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from ....common.mini_jei import (
    RecipesCollection,
    RecipeBase,
    CategoryType,
    GetRecipesByInput,
    GetRecipesByOutput,
)
from .recipe_checker_ui import RecipeCheckerUI


def CheckRecipe(item_id, category=CategoryType.ITEM):
    # type: (str, str) -> RecipeCheckerUI | None
    recipes = GetRecipesByOutput(category, item_id)
    if not recipes:
        return None
    return PushRecipeCheckerUI(recipes)


def CheckUsage(item_id, category=CategoryType.ITEM):
    # type: (str, str) -> RecipeCheckerUI | None
    recipes = GetRecipesByInput(category, item_id)
    if not recipes:
        return None
    return PushRecipeCheckerUI(recipes)


def PushRecipeCheckerUI(recipes):
    # type: (RecipesCollection[RecipeBase] | list[RecipeBase]) -> RecipeCheckerUI
    if len(recipes) == 0:
        raise ValueError("Can't push an empty recipe list")
    recipe_list = recipes.list() if isinstance(recipes, RecipesCollection) else recipes
    recipe_ins = recipe_list[0]
    recipe_renderer = recipe_ins.GetRenderer()
    if recipe_renderer is None:
        raise ValueError(
            "Can't push a recipe without a renderer :: %s" % recipe_ins.cls_name
        )
    uiNode = RecipeCheckerUI.PushUI({
        "recipes": [
            (
                recipe_ins.recipe_icon_id,
                recipe_renderer.minijei_title
                or GetItemHoverName(recipe_ins.recipe_icon_id),
                recipe_list,
            )
        ]
    })
    return uiNode


def AsRecipeCheckerBtn(
    ctrl,  # type: UButton
    recipes,  # type: RecipesCollection
):
    def cb(params):
        PushRecipeCheckerUI(recipes)

    ctrl.SetCallback(cb)
