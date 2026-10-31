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

    与 MEI 共用 MachineRecipeLib.VacuumFreezer 内容布局。
    基类按真实槽位映射物品和流体；温度条件与升级要求显示在进度提示中。
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
        self.UpdatePower(panel, 1.0, self.PowerTip())


VacuumFreezerRecipe.SetRenderer(VacuumFreezerRecipeRenderer)
