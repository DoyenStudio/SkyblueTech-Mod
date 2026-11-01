# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.allitems_getter import GetItemsByTag
from .define import RecipeBase, CategoryType
from .storage import recipesFrom, recipesTo, recipesOf


def _get_index_recipes(index, category, id):
    # type: (dict[str, set[RecipeBase]], str, str) -> list[RecipeBase]
    recipes = set(index.get(id, ()))
    if category == CategoryType.ITEM and not id.startswith("tag:"):
        # 与机器匹配、标签候选列表使用同一份物品/方块标签并集。
        for key, tagged_recipes in index.items():
            if key.startswith("tag:") and id in GetItemsByTag(key[4:]):
                recipes.update(tagged_recipes)
    return list(recipes)


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
    if category == CategoryType.ITEM and not id.startswith("tag:"):
        from ..common.vanilla import LoadItemRecipes

        LoadItemRecipes(id, get_output=True)
    return _get_index_recipes(recipesFrom.get(category, {}), category, id)


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
    return _get_index_recipes(recipesTo.get(category, {}), category, id)


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
