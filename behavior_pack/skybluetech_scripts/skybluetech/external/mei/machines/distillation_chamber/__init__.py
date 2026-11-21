# coding=utf-8
"""
小型蒸馏仓（`distillation_chamber`）—— 流体 → 流体（连续过程，不耗电）。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/DistillationChamber.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 机器右边的温度数据板不画（规范 v2 §12.5）：最适温度、温度范围进箭头的悬停（`Data["conditions"]`）。
典型配方：**50 mB 水 → 45 mB 蒸馏水**
"""
from .._common import BuildMachine
from ... import exports
from .._common import Kelvin

CATEGORY_ID = "skybluetech:distillation_chamber"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "DistillationChamberRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 117

def Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    min_temperature = int(sb_recipe.min_temperature)
    max_temperature = int(sb_recipe.max_temperature)
    fit_temperature = int(sb_recipe.fit_temperature)
    conditions = ["§7最适温度： §f" + Kelvin(fit_temperature)]
    if sb_recipe.max_temperature == sb_recipe.fit_temperature:
        conditions.extend([
            "§7起步温度： §f> %d K" % min_temperature,
            "§7满速以上进出料率同比封顶",
            "§7配方用量满速耗时： §f%d tick" % sb_recipe.tick_duration,
            "§7配方用量热耗： §f%g RF热" % (sb_recipe.produce * sb_recipe.heat_per_produce),
        ])
    else:
        conditions.append("§7温度范围： §f%d ~ %d K" % (min_temperature, max_temperature))
    parts["data"].update(min_temperature=min_temperature, max_temperature=max_temperature,
                         fit_temperature=fit_temperature, conditions=conditions)


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.distillation_chamber",
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=Decorate,
    )
