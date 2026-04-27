# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.distillation_chamber import (
    DistillationChamberRecipe,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FormatKelvin
from .define import MachineRecipeRendererBase


class DistillationChamberRecipeRenderer(MachineRecipeRendererBase):
    recipe_icon_id = machinery.DISTILLATION_CHAMBER
    render_ui_def_name = "RecipeCheckerLib.distillation_chamber_recipes"

    def __init__(self, recipe):
        # type: (DistillationChamberRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipeRendererBase.RenderInit(self, panel)
        panel["right_board/tip_text"].asLabel().SetText(
            FormatKelvin(self.recipe.fit_temperature)
        )
        panel["right_board/tip_text2"].asLabel().SetText(
            "> %s\n< %s"
            % (
                FormatKelvin(self.recipe.min_temperature),
                FormatKelvin(self.recipe.max_temperature),
            )
        )


DistillationChamberRecipe.SetRenderer(DistillationChamberRecipeRenderer)
