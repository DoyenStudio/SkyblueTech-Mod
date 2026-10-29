# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.gas_burning_generator import (
    GasBurningGeneratorRecipe,
)
from .define import GeneratorRecipeRenderer


class GasBurningGeneratorRecipeRenderer(GeneratorRecipeRenderer):
    recipe_icon_id = machinery.Machinery.GAS_BURNING_GENERATOR
    render_ui_def_name = "RecipeCheckerLib.gas_burning_generator_recipes"

    def __init__(self, recipe):
        # type: (GasBurningGeneratorRecipe) -> None
        GeneratorRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        from ...ui.machinery.utils import SetHoverText

        GeneratorRecipeRenderer.RenderInit(self, panel)
        # 没有废气产出的配方: 在废气槽 (fluid1) 的悬停里写明 (同 MEI 配方页)
        if self.recipe.output_gas_id is None:
            SetHoverText(panel["fluid1"], "§7没有废气")


GasBurningGeneratorRecipe.SetRenderer(GasBurningGeneratorRecipeRenderer)
