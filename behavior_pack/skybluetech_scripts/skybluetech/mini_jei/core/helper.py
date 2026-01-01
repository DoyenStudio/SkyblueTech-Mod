# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from skybluetech_scripts.tooldelta.api.client import GetItemHoverName, GetItemTags
from .define import RecipeBase, CategoryType
from .storage import *

def GetRecipesByOutput(category, id):
    # type: (str, str) -> list[RecipeBase]
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
    res = recipesTo.get(category, {}).get(id, [])
    if category is not CategoryType.ITEM or not id.startswith("tag:"):
        # 还需要根据 tag 找配方
        tags = GetItemTags(id)
        res += [
            recipe
            for tag in tags
            for recipe in GetRecipesByOutput(CategoryType.ITEM, "tag:" + tag)
        ]
    return res

def GetRecipesByCategory(category):
    # type: (str) -> list[RecipeBase]
    return recipesOf.get(category, [])