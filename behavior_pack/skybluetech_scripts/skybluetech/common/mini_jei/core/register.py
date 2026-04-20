# coding=utf-8
from .define import RecipeBase, Description
from .storage import recipesFrom, recipesTo, recipesOf

recipes_registered = set()  # type: set[RecipeBase]


def RegisterRecipe(recipe):
    # type: (RecipeBase) -> None
    "注册配方。"
    if recipe in recipes_registered:
        return
    for category, inputs in recipe.GetInputs().items():
        for input in inputs:
            recipesTo.setdefault(category, {}).setdefault(input, []).append(recipe)
            # if recipe in rcps:
            #     print("1:add multiple recipe")
            #     # continue
    for category, outputs in recipe.GetOutputs().items():
        for output in outputs:
            recipesFrom.setdefault(category, {}).setdefault(output, []).append(recipe)
            # if recipe in rcps:
            #     print("2:add multiple recipe")
            #     # continue
    recipesOf.setdefault(recipe.recipe_icon_id, []).append(recipe)
    # if recipe in rcps:
    #     print("3:add multiple recipe")
    #     # return


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
