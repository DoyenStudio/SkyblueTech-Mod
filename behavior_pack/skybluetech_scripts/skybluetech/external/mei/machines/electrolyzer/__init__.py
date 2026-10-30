# coding=utf-8
"""
电解机（`electrolyzer`）—— 流体 → 流体 ×2（配方类还支持阳极原料、阴极产物、副产物与第三种流体）。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/Electrolyzer.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 机器的内容区本来就是满的，配方行 170 宽（四周留白），是蔚蓝最宽的一页 —— MEI 的配方页按最宽的一行撑开。
典型配方：**4 mB 水 → 20 mB 氧气 + 40 mB 氢气**（480 RF/t × 10 刻）
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:electrolyzer"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "ElectrolyzerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 128


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.electrolyzer",
        recipes=recipes,
        sort_index=SORT_INDEX,
    )
