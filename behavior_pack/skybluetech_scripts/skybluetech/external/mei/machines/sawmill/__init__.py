# coding=utf-8
"""
锯木机（`sawmill`）—— 1 进 2 出（副产物带概率）。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/Sawmill.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 副产物的概率在 Ingredient 上（`Output.prob`），配方页的悬停多一行「概率」（`_common.ChanceText`）。
> 第 3 号产出格 37 条配方都不用，照机器预留（画成空格）。
典型配方：**橡木原木 → 6 橡木木板 + 锯末（20%）**
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:sawmill"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "SawmillRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 108


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.sawmill",
        recipes=recipes,
        sort_index=SORT_INDEX,
    )
