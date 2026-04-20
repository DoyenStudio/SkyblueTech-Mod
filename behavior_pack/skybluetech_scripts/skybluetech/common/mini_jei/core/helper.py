# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetItemTags
from .define import RecipeBase, CategoryType
from .storage import recipesFrom, recipesTo, recipesOf
from .vanilla import LoadItemRecipes


def GetRecipesByOutput(category, id):
    # type: (str, str) -> list[RecipeBase]
    if category == CategoryType.ITEM:
        LoadItemRecipes(id)
    res = recipesFrom.get(category, {}).get(id, [])
    if category is not CategoryType.ITEM or not id.startswith("tag:"):
        # 还需要根据 tag 找配方
        tags = GetItemTags(id)
        res += [
            recipe
            for tag in tags
            for recipe in GetRecipesByOutput(CategoryType.ITEM, "tag:" + tag)
        ]
    return res


def GetRecipesByInput(category, id):
    # type: (str, str) -> list[RecipeBase]
    if category == CategoryType.ITEM:
        LoadItemRecipes(id)
    res = recipesTo.get(category, {}).get(id, [])
    if category is not CategoryType.ITEM or not id.startswith("tag:"):
        # 还需要根据 tag 找配方
        tags = GetItemTags(id)
        res += [
            recipe
            for tag in tags
            for recipe in GetRecipesByInput(CategoryType.ITEM, "tag:" + tag)
        ]
    return res


def GetRecipesByCategory(category):
    # type: (str) -> list[RecipeBase]
    "WARNING: 目前暂时无法对工作台、 熔炉等原版配方使用。"
    return recipesOf.get(category, [])
