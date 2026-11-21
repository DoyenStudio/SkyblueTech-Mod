# coding=utf-8
from ....common.machinery_def.effluent_outfall import EffluentOutfallRecipe
from .define import _AnimatedRenderer


class EffluentOutfallRecipeRenderer(_AnimatedRenderer):
    recipe_icon_id = EffluentOutfallRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.effluent_outfall_recipes"

    def RenderInit(self, panel):
        _AnimatedRenderer.RenderInit(self, panel)
        self.GetControl(panel, "content/body/rate").asLabel().SetText(self.recipe.RateText())

    def ProgressTip(self):
        return [self.recipe.BiomeText()]


EffluentOutfallRecipe.SetRenderer(EffluentOutfallRecipeRenderer)
