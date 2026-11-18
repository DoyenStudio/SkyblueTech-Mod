# coding=utf-8
from ....common.mini_jei.machinery.gas_metallurgical_furnace import GasMetallurgicalFurnaceRecipe
from .define import MachineRecipeRenderer


class GasMetallurgicalFurnaceRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = GasMetallurgicalFurnaceRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.gas_metallurgical_furnace_controller_recipes"

    def PowerTotal(self):
        return self.recipe.total_rf

    def ProgressTip(self):
        return [self.recipe.title, "§7整批耗电：§f%d RF" % self.recipe.total_rf,
                "§7原热耗已折算为电耗；整批投料与结算"]


GasMetallurgicalFurnaceRecipe.SetRenderer(GasMetallurgicalFurnaceRecipeRenderer)
