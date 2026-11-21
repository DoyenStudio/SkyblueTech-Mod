# coding=utf-8
from skybluetech_scripts.tooldelta.ui.elem_comp import UBaseCtrl
from skybluetech_scripts.skybluetech.common.define.id_enum import machinery
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.distillation_chamber import (
    DistillationChamberRecipe,
)
from skybluetech_scripts.skybluetech.client.ui.machinery.utils import FormatKelvin
from .define import MachineRecipeRendererBase, _AnimatedRenderer


class DistillationChamberRecipeRenderer(_AnimatedRenderer):
    """蒸馏是连续过程 (不走进度): 静态箭头, 温度要求写进箭头的悬停 (同 MEI 配方页)。"""

    recipe_icon_id = machinery.Machinery.DISTILLATION_CHAMBER
    render_ui_def_name = "RecipeCheckerLib.distillation_chamber_recipes"
    render_progress = False

    def __init__(self, recipe):
        # type: (DistillationChamberRecipe) -> None
        MachineRecipeRendererBase.__init__(self, recipe)
        self.recipe = recipe

    def ProgressTip(self):
        if self.recipe.max_temperature == self.recipe.fit_temperature:
            return [
                "§7起步温度： §f> " + FormatKelvin(self.recipe.min_temperature),
                "§7满速温度： §f" + FormatKelvin(self.recipe.fit_temperature),
                "§7满速以上进出料率同比封顶",
                "§7配方用量满速耗时： §f%d tick" % self.recipe.tick_duration,
                "§7配方用量热耗： §f%g RF热"
                % (self.recipe.produce * self.recipe.heat_per_produce),
            ]
        return [
            "§7最适温度： §f" + FormatKelvin(self.recipe.fit_temperature),
            "§7温度范围： §f%s ~ %s"
            % (FormatKelvin(self.recipe.min_temperature), FormatKelvin(self.recipe.max_temperature)),
        ]


DistillationChamberRecipe.SetRenderer(DistillationChamberRecipeRenderer)
