# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.gas_burning_generator import (
    GasBurningGeneratorRecipe,
)
from .define import GeneratorRecipeRenderer


class GasBurningGeneratorRecipeRenderer(GeneratorRecipeRenderer):
    recipe_icon_id = machinery.GAS_BURNING_GENERATOR
    render_ui_def_name = "RecipeCheckerLib.gas_burning_generator_recipes"

    def __init__(self, recipe):
        # type: (GasBurningGeneratorRecipe) -> None
        GeneratorRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        GasBurningGeneratorRecipeRenderer.RenderInit(self, panel)
        panel["garbage_gas_tip"].SetVisible(self.recipe.output_gas_id is None)


GasBurningGeneratorRecipe.SetRenderer(GasBurningGeneratorRecipeRenderer)
