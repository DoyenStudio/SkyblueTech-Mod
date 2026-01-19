# coding=utf-8
from .define import RecipeBase, Description
from .storage import recipesFrom, recipesTo, recipesOf


def RegisterRecipe(recipe):
    # type: (RecipeBase) -> None
    "注册配方。"
    for category, inputs in recipe.GetInputs().items():
        for input in inputs:
            rcps = recipesTo.setdefault(category, {}).setdefault(input, [])
            # if recipe in rcps:
            #     print("1:add multiple recipe")
            #     # continue
            rcps.append(recipe)
    for category, outputs in recipe.GetOutputs().items():
        for output in outputs:
            rcps = recipesFrom.setdefault(category, {}).setdefault(output, [])
            # if recipe in rcps:
            #     print("2:add multiple recipe")
            #     # continue
            rcps.append(recipe)
    rcps = recipesOf.setdefault(recipe.recipe_icon_id, [])
    # if recipe in rcps:
    #     print("3:add multiple recipe")
    #     # return
    rcps.append(recipe)

def RegisterDescription(categories_with_ids, title, content):
    # type: (dict[str, list[str]], str, str) -> None
    """
    注册描述。

    Args:
        categories_with_ids (dict[str, list[str]]): 被描述物分组: 分组内被描述物列表
        title (str): 标题
        content (str): 正文内容
    """
    RegisterRecipe(Description(categories_with_ids, title, content.replace(" ", u"\u00a0")))
