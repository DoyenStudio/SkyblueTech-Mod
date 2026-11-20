# coding=utf-8
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.high_temp_electrolyzer import HighTempElectrolyzerRecipe
from skybluetech_scripts.skybluetech.client.mini_jei.machinery.define import MachineRecipeRenderer


class HighTempElectrolyzerRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = HighTempElectrolyzerRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.high_temp_electrolyzer_recipes"

    def ProgressTip(self):
        return self.recipe.conditions()


HighTempElectrolyzerRecipe.SetRenderer(HighTempElectrolyzerRecipeRenderer)
