# coding=utf-8
from .define import RecipeBase, Description
from .storage import recipesFrom, recipesTo, recipesOf

recipes_registered = set()  # type: set[RecipeBase]


def RegisterRecipe(recipe):
    # type: (RecipeBase) -> None
    "注册配方。"
    if recipe in recipes_registered:
        return
    # 使用 set, 避免重复配方 (从配方页进入子配方再退出会注册重复配方)
    for category, inputs in recipe.GetInputs().items():
        for input in inputs:
            recipesTo.setdefault(category, {}).setdefault(input, set()).add(recipe)
    for category, outputs in recipe.GetOutputs().items():
        for output in outputs:
            recipesFrom.setdefault(category, {}).setdefault(output, set()).add(recipe)
    recipesOf.setdefault(recipe.recipe_icon_id, set()).add(recipe)


def RegisterDescription(categories_with_ids, title, content):
    # type: (dict[str, list[str]], str, str) -> None
    """
    注册描述。

    Args:
        categories_with_ids (dict[str, list[str]]): 被描述物分组: 分组内被描述物列表
        title (str): 标题
        content (str): 正文内容
    """
    RegisterRecipe(
        Description(categories_with_ids, title, content.replace(" ", "\u00a0"))
    )
