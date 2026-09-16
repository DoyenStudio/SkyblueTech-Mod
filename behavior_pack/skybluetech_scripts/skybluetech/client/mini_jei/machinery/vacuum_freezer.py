# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.vacuum_freezer import (
    VacuumFreezerRecipe,
)
from .define import MachineRecipeRenderer


def FormatRecipeKelvin(kelvin):
    # type: (float) -> str
    """按右侧面板的占位样式显示温度: 整数不带小数点, 小数最多两位, 末尾跟 " K"。

    面板里两个温度值的占位文本是 "0 K", 所以这里也照这个样式填值, 例如
    "100 K" / "80 K" / "77.5 K", 而不是 FormatKelvin 的 "100.00 K"。
    """
    return ("%.2f" % kelvin).rstrip("0").rstrip(".") + " K"


class VacuumFreezerRecipeRenderer(MachineRecipeRenderer):
    """真空冷却仓配方页。

    面板定义见 MiniJEI 的 `RecipeCheckerLib.vacuum_freezer_recipes`: 左半是流体/物品槽,
    中间是进度条(由基类按 `tick_duration` 循环推进), 右侧板显示两个温度:

        - 冷凝温度上限 `max_temperature`: 高于它配方完全不推进
        - 最佳冷凝温度 `fit_temperature`: 到它以下按最快速度推进

    两个温度都由配方自带, 每个配方可以不一样, 所以在这里按配方填数。

    物品槽与流体槽由基类的 `RenderInit` 统一填: 物品走 `slot0`/`slot1`(带数量、概率、
    点开查用途), 流体走 `fluid0`/`fluid1`。真空冷却仓的配方本身同时支持物品与流体,
    只是现在还没有需要物品的配方 —— 物品这条链路要一直保留, 不能因为暂时用不到就省掉。
    """

    recipe_icon_id = machinery.Machinery.VACUUM_FREEZER
    render_ui_def_name = "RecipeCheckerLib.vacuum_freezer_recipes"

    def __init__(self, recipe):
        # type: (VacuumFreezerRecipe) -> None
        MachineRecipeRenderer.__init__(self, recipe)
        self.recipe = recipe

    def RenderInit(self, panel):
        # type: (UBaseCtrl) -> None
        MachineRecipeRenderer.RenderInit(self, panel)
        panel["right_board/max_kelvin"].asLabel().SetText(
            FormatRecipeKelvin(self.recipe.max_temperature)
        )
        panel["right_board/fit_kelvin"].asLabel().SetText(
            FormatRecipeKelvin(self.recipe.fit_temperature)
        )


VacuumFreezerRecipe.SetRenderer(VacuumFreezerRecipeRenderer)
