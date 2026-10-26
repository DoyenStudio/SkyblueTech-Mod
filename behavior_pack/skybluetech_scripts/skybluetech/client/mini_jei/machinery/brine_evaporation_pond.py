# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import BrineEvaporationPond
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.brine_evaporation_pond import (
    BrineEvaporationPondRecipe,
)
from skybluetech_scripts.skybluetech.client.mini_jei.machinery.define import (
    MachineRecipeRendererBase,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FormatKelvin


class BrineEvaporationPondRecipeRenderer(MachineRecipeRendererBase):
    recipe_icon_id = BrineEvaporationPond.CONTROLLER
    render_ui_def_name = "RecipeCheckerLib.distillation_chamber_recipes"

    def RenderInit(self, panel):
        MachineRecipeRendererBase.RenderInit(self, panel)
        panel["right_board/tip_text"].asLabel().SetText(
            FormatKelvin(self.recipe.fit_temperature)
        )
        panel["right_board/tip_text2"].asLabel().SetText(
            "最低 %gK\n热耗 %g/次"
            % (self.recipe.min_temperature, self.recipe.heat_cost)
        )


BrineEvaporationPondRecipe.SetRenderer(BrineEvaporationPondRecipeRenderer)
