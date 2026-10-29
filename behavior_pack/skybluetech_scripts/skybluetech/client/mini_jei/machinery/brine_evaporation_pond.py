# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import BrineEvaporationPond
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.brine_evaporation_pond import (
    BrineEvaporationPondRecipe,
)
from skybluetech_scripts.skybluetech.client.mini_jei.machinery.define import (
    _AnimatedRenderer,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FormatKelvin


class BrineEvaporationPondRecipeRenderer(_AnimatedRenderer):
    """蒸发是连续过程 (不走进度): 静态箭头, 温度要求与耗热写进箭头的悬停 (同 MEI 配方页)。"""

    recipe_icon_id = BrineEvaporationPond.CONTROLLER
    render_ui_def_name = "RecipeCheckerLib.brine_evaporation_pond_recipes"
    render_progress = False

    def ProgressTip(self):
        return [
            "§7最适温度： §f" + FormatKelvin(self.recipe.fit_temperature),
            "§7最低温度： §f" + FormatKelvin(self.recipe.min_temperature),
            "§7每次耗热： §f%g" % self.recipe.heat_cost,
        ]


BrineEvaporationPondRecipe.SetRenderer(BrineEvaporationPondRecipeRenderer)
