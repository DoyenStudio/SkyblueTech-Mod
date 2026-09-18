# coding=utf-8
from skybluetech_scripts.skybluetech.common.mini_jei import (
    CategoryType,
    GetRecipesByInput,
    GetRecipesByOutput,
    RecipeBase,
    RecipesCollection,
)
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName
from skybluetech_scripts.tooldelta.ui.elem_comp import UButton

from .recipe_checker_ui import RecipeCheckerUI
from .utils import RecipeCategoriesData, RecipePageData


def _GroupRecipesByRenderer(recipes):
    # type: (list[RecipeBase]) -> RecipeCategoriesData
    grouped_recipes = {}
    grouped_recipe_keys = []
    for recipe in recipes:
        recipe_renderer_cls = recipe.GetRenderer()
        if recipe_renderer_cls is None:
            raise ValueError(
                "Can't push a recipe without a renderer :: %s" % recipe.cls_name
            )
        recipe_icon_id = recipe_renderer_cls.recipe_icon_id
        recipe_title = recipe_renderer_cls.minijei_title or GetItemHoverName(
            recipe_icon_id
        )
        key = (recipe_icon_id, recipe_title)
        if key not in grouped_recipes:
            grouped_recipes[key] = []
            grouped_recipe_keys.append(key)
        grouped_recipes[key].append(recipe)
    return RecipeCategoriesData([
        RecipePageData(
            recipe_icon_id,
            recipe_title,
            grouped_recipes[(recipe_icon_id, recipe_title)],
        )
        for recipe_icon_id, recipe_title in grouped_recipe_keys
    ])


def CheckRecipe(item_id, category=CategoryType.ITEM):
    # type: (str, str) -> RecipeCheckerUI | None
    recipes = GetRecipesByOutput(category, item_id)
    if not recipes:
        return None
    return PushRecipeCheckerUI(recipes)


def CheckRecipes(item_ids, category=CategoryType.ITEM):
    # type: (list[str], str) -> RecipeCheckerUI | None
    recipes = [
        rcp for item_id in item_ids for rcp in GetRecipesByOutput(category, item_id)
    ]
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
    return RecipeCheckerUI.Display(_GroupRecipesByRenderer(recipe_list))


def AsRecipeCheckerBtn(
    ctrl,  # type: UButton
    recipes,  # type: RecipesCollection
):
    def cb(params):
        PushRecipeCheckerUI(recipes)

    ctrl.SetCallback(cb)
