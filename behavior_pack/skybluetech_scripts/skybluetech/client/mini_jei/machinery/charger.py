# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.charger import (
    ChargerRecipe,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl

from .define import MachineRecipeRenderer


class ChargerRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = machinery.Machinery.CHARGER
    render_ui_def_name = "RecipeCheckerLib.charger_recipes"

    def __init__(self, recipe):
        # type: (ChargerRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        from ...ui.machinery.utils import FormatRF

        MachineRecipeRenderer.RenderInit(self, panel)
        panel["energy_cost"].asLabel().SetText(
            "%s\n%s/t"
            % (
                FormatRF(self.recipe.power_cost * self.recipe.tick_duration),
                FormatRF(self.recipe.power_cost),
            )
        )


ChargerRecipe.SetRenderer(ChargerRecipeRenderer)
