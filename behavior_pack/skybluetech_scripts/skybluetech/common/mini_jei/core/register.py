# coding=utf-8
from .define import RecipeBase
from .storage import recipesFrom, recipesTo, recipesOf

recipes_registered = set()  # type: set[RecipeBase]


def RegisterRecipe(recipe):
    # type: (RecipeBase) -> None
    """
    注册配方。 如果把配方放入配方组内则无需额外注册。

    Args:
        recipe (RecipeBase): 配方对象
    """
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
