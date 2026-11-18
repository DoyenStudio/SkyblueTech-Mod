# coding=utf-8
from ....common.mini_jei.machinery.flotation_machine import FlotationMachineRecipe
from ....common.machinery_def.flotation_machine import recipes as _recipes
from .define import MachineRecipeRenderer


class FlotationMachineRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = FlotationMachineRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.flotation_machine_recipes"


FlotationMachineRecipe.SetRenderer(FlotationMachineRecipeRenderer)
