# coding=utf-8
from skybluetech_scripts.tooldelta.api.client import GetItemTags
from .define import RecipeBase, CategoryType
from .storage import recipesFrom, recipesTo, recipesOf


def GetRecipesByOutput(category, id):
    # type: (str, str) -> list[RecipeBase]
    """
    通过输出获取配方列表。

    Args:
        category (str): Category 枚举
        id (str): 配方物 ID, 如果以 "tag:" 开头则代表为标签物

    Returns:
        list[RecipeBase]: 配方列表
    """
    if category == CategoryType.ITEM:
        from ..common.vanilla import LoadItemRecipes

        LoadItemRecipes(id, get_output=True)
    res = list(recipesFrom.get(category, {}).get(id, set()))
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
    """
    通过输入获取配方列表。

    Args:
        category (str): Category 枚举
        id (str): 配方物 ID, 如果以 "tag:" 开头则代表为标签物

    Returns:
        list[RecipeBase]: 配方列表
    """
    if category == CategoryType.ITEM and not id.startswith("tag:"):
        from ..common.vanilla import LoadItemRecipes

        LoadItemRecipes(id, get_input=True)
    res = list(recipesTo.get(category, {}).get(id, []))
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
    """
    通过一个类别里的所有配方。

    WARNING: 目前暂时无法对工作台、 熔炉等原版配方使用。

    Args:
        category (str): Category 枚举

    Returns:
        list[RecipeBase]: 配方列表
    """
    return list(recipesOf.get(category, []))
