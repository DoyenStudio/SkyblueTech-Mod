# coding=utf-8
from ....common.mini_jei.machinery.specialized_growth_chamber import (
    CATALYST_SLOTS,
    SpecializedGrowthChamberRecipe,
)
from .define import MachineRecipeRenderer


class SpecializedGrowthChamberRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = SpecializedGrowthChamberRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.specialized_growth_chamber_recipes"

    def GetSlotControl(self, panel, kind, slot, outputs=False):
        if kind == "item" and not outputs and slot in CATALYST_SLOTS:
            return self.GetCatalystControl(panel, CATALYST_SLOTS.index(slot), "slot%d" % slot)
        return MachineRecipeRenderer.GetSlotControl(self, panel, kind, slot, outputs)

    def ProgressTip(self):
        return ["§7作物与培养基不消耗"]


SpecializedGrowthChamberRecipe.SetRenderer(SpecializedGrowthChamberRecipeRenderer)
