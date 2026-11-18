# coding=utf-8
from ....common.mini_jei.machinery.industrial_centrifuge import IndustrialCentrifugeRecipe
from ....common.machinery_def.industrial_centrifuge import recipes as _recipes
from .define import MachineRecipeRenderer


class IndustrialCentrifugeRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = IndustrialCentrifugeRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.industrial_centrifuge_downside_recipes"

    def ProgressTip(self):
        return self.recipe.heat_conditions()


IndustrialCentrifugeRecipe.SetRenderer(IndustrialCentrifugeRecipeRenderer)
