# coding=utf-8
from ....common.mini_jei.machinery.oilfuel_generator import OilFuelGeneratorRecipe
from .define import GeneratorRecipeRenderer


class OilFuelGeneratorRecipeRenderer(GeneratorRecipeRenderer):
    recipe_icon_id = OilFuelGeneratorRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.oilfuel_generator_recipes"


OilFuelGeneratorRecipe.SetRenderer(OilFuelGeneratorRecipeRenderer)
