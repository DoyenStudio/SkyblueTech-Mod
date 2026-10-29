# coding=utf-8
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.air_compressor import (
    AirCompressorRecipe,
)
from skybluetech_scripts.skybluetech.common.machinery_def.air_compressor import (
    GetDimensionName,
    recipes as _recipes,  # noqa: F401
)
from .define import MachineRecipeRenderer


def GetFluidDisplayName(fluid_id):
    # type: (str | None) -> str
    if fluid_id is None:
        return "无"
    try:
        return Item(fluid_id).GetBasicInfo().itemName or fluid_id
    except Exception:
        return fluid_id


class AirCompressorRecipeRenderer(MachineRecipeRenderer):
    recipe_icon_id = machinery.Machinery.AIR_COMPRESSOR
    render_ui_def_name = "RecipeCheckerLib.air_compressor_recipes"

    def __init__(self, recipe):
        # type: (AirCompressorRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def ProgressTip(self):
        # 维度与产出的空气种类写进进度悬停 (同 MEI 配方页)
        return [
            "§7维度： §f" + GetDimensionName(self.recipe.dimension),
            "§7产出： §f" + GetFluidDisplayName(self.recipe.output_fluid_id),
        ]


AirCompressorRecipe.SetRenderer(AirCompressorRecipeRenderer)
