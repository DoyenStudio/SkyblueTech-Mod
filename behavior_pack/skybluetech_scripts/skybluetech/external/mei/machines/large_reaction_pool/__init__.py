# coding=utf-8
from .._common import BuildMachine
from ... import exports


def _decorate(recipe, parts):
    parts["data"]["conditions"] = recipe.conditions()


def Build():
    icon_id, recipes = exports.Collection("LargeReactionPoolRecipe")
    return BuildMachine(category_id=icon_id, icon_id=icon_id,
                        name_key="skybluetech.mei.category.large_reaction_pool",
                        recipes=recipes, sort_index=126, decorate=_decorate)
