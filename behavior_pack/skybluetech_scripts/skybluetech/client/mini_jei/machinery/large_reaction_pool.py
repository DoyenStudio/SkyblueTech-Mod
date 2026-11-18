# coding=utf-8
from ....common.mini_jei.machinery.large_reaction_pool import LargeReactionPoolRecipe
from .define import MachineRecipeRenderer


class LargeReactionPoolRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = LargeReactionPoolRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.large_reaction_pool_controller_recipes"

    def ProgressTip(self):
        return self.recipe.conditions()


LargeReactionPoolRecipe.SetRenderer(LargeReactionPoolRecipeRenderer)
