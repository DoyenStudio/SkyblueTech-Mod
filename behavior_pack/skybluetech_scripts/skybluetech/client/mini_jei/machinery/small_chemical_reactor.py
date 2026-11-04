# coding=utf-8
from ....common.mini_jei.machinery.small_chemical_reactor import SmallChemicalReactorRecipe
from .define import MachineRecipeRenderer


class SmallChemicalReactorRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = SmallChemicalReactorRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.small_chemical_reactor_recipes"

    def GetSlotControl(self, panel, kind, slot, outputs=False):
        if kind == "item" and slot == 2 and not outputs:
            return self.GetCatalystControl(panel, 0, "slot2")
        return MachineRecipeRenderer.GetSlotControl(self, panel, kind, slot, outputs)

    def ProgressTip(self):
        return ["§7催化剂不消耗"]


SmallChemicalReactorRecipe.SetRenderer(SmallChemicalReactorRecipeRenderer)
