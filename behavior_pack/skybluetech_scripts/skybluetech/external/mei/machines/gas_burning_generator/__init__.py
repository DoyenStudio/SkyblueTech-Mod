# coding=utf-8
"""
小型燃气发电机（`gas_burning_generator`）—— 流体 → RF（+ 废气）。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/GasBurningGenerator.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 一 tick 烧一次的连续过程：配方页不走动画、火焰点着、能量条满格（`_common.CONTINUOUS_TICKS`）。
典型配方：**4 mB 甲烷 → 160 RF/t**（一 tick 烧一次，连续）
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:gas_burning_generator"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "GasBurningGeneratorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 121


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.gas_burning_generator",
        recipes=recipes,
        sort_index=SORT_INDEX,
    )
