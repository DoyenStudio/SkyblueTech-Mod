# coding=utf-8
from ....common.mini_jei.machinery.heat_melting_chamber import HeatMeltingChamberRecipe
from .define import _AnimatedRenderer


class HeatMeltingChamberRecipeRenderer(_AnimatedRenderer):
    recipe_icon_id = HeatMeltingChamberRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.heat_melting_chamber_recipes"

    def ProgressTip(self):
        r = self.recipe
        return [
            "最低 / 最适 / 最高温度： %g / %g / %g K" % (
                r.min_temperature, r.fit_temperature, r.max_temperature),
            "§7[§e!§7] §7过热会导致流体§e直接蒸发散失",
        ]


HeatMeltingChamberRecipe.SetRenderer(HeatMeltingChamberRecipeRenderer)
