# coding=utf-8
from ....common.mini_jei.machinery.thermal_cracker import ThermalCrackerRecipe
from .define import MachineRecipeRenderer


class ThermalCrackerRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = ThermalCrackerRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.thermal_cracker_recipes"
    render_progress = False

    def ProgressTip(self):
        recipe = self.recipe
        return ["流体数量为每批用量；200 tick / 份",
                "%g K < T ≤ %g K；%g K 满速" % (recipe.min_temperature, recipe.max_temperature, recipe.fit_temperature),
                "每批耗热 %g RF热；外部供热；两路副产物均不能堵塞" % recipe.heat_cost]


ThermalCrackerRecipe.SetRenderer(ThermalCrackerRecipeRenderer)
