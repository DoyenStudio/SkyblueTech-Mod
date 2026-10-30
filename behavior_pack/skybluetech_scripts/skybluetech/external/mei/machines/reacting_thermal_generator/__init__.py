# coding=utf-8
"""
热力反应发电机（`reacting_thermal_generator`）—— 流体 + 物 → RF + 流体。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/ReactingThermalGenerator.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
典型配方：**250 mB 水 + 硫 → 45 RF/t + 250 mB 硫酸**
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:reacting_thermal_generator"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "ReactingThermalGeneratorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 122


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.reacting_thermal_generator",
        recipes=recipes,
        sort_index=SORT_INDEX,
    )
