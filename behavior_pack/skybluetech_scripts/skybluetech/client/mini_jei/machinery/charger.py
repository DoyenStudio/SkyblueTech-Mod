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

    # 耗能由基类 MachineRecipeRenderer 画在能量条上并写进其悬停


ChargerRecipe.SetRenderer(ChargerRecipeRenderer)
