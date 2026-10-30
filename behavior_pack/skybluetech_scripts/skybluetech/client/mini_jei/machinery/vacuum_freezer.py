# coding=utf-8
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FormatKelvin
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.vacuum_freezer import (
    VacuumFreezerRecipe,
)
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl

from ...ui.recipe_checker.render_utils import ItemDisplayer
from .define import MachineRecipeRenderer


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

    # 温度要求与所需的机器升级写进进度悬停 (同 MEI 配方页); 配方功率为 0, 实际耗电取决于机器设定的温度

    def ProgressTip(self):
        lines = [
            "§7温度： §f≤ %s（最适 %s）"
            % (FormatKelvin(self.recipe.max_temperature), FormatKelvin(self.recipe.fit_temperature))
        ]
        if self.recipe.extra_upgrader_id is not None:
            name = Item(self.recipe.extra_upgrader_id).GetBasicInfo().itemName or self.recipe.extra_upgrader_id
            lines.append("§e需要机器升级： §f" + name)
        return lines

    def PowerTip(self):
        return "§7耗能： §f随设定温度变化"

    def RenderPower(self, panel, p):
        from ...ui.machinery.utils import UpdatePowerBar

        UpdatePowerBar(panel["power_bar"], 1, 1, hover=self.PowerTip())


VacuumFreezerRecipe.SetRenderer(VacuumFreezerRecipeRenderer)
