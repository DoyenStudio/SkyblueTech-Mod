# coding=utf-8
from .define import RecipeBase
from .storage import recipesFrom, recipesTo, recipesOf


def RegisterRecipe(recipe):
    # type: (RecipeBase) -> None
    for category, inputs in recipe.GetInputs().items():
        for input in inputs:
            recipesTo.setdefault(category, {}).setdefault(input, []).append(recipe)
    for category, outputs in recipe.GetOutputs().items():
        for output in outputs:
            recipesFrom.setdefault(category, {}).setdefault(output, []).append(recipe)
    recipesOf.setdefault(recipe.recipe_icon_id, []).append(recipe)

