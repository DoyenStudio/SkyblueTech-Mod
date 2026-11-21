# coding=utf-8
from ....common.mini_jei.machinery.thermal_cracker import ThermalCrackerRecipe
from ...ui.machinery.utils import SetHoverText, UpdateProgress
from .define import MachineRecipeRenderer


class ThermalCrackerRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = ThermalCrackerRecipe.recipe_icon_id
    render_ui_def_name = "RecipeCheckerLib.thermal_cracker_recipes"

    def __init__(self, recipe):
        MachineRecipeRenderer.__init__(self, recipe)
        self.render_progress = bool(recipe.recipe_id)

    def RenderInit(self, panel):
        for side, values in (("inputs", self.GetDisplayInputs()), ("outputs", self.GetDisplayOutputs())):
            for kind, slot in self.layout[side]:
                self.GetSlotControl(panel, kind, slot, outputs=side == "outputs").SetVisible(
                    slot in values.get(kind, {})
                )
        MachineRecipeRenderer.RenderInit(self, panel)
        UpdateProgress(self.GetControl(panel, "progress"), 0.0)
        SetHoverText(self.GetControl(panel, "progress_tip"), "\n".join(self.recipe.conditions()))

    def ProgressTip(self):
        return self.recipe.conditions()


ThermalCrackerRecipe.SetRenderer(ThermalCrackerRecipeRenderer)
