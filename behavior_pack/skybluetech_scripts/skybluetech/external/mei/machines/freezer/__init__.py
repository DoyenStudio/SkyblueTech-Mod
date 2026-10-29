# coding=utf-8
"""
冷冻机（`freezer`）—— 流体 → 物。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/Freezer.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 选产物的按钮不画（配方行缩成 S 档，流体槽 36×54，产物格与进度跟它居中，同流体冷却机）。
典型配方：**250 mB 水 → 雪球**（40 RF/t × 20 刻）
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:freezer"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "FreezerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 113

OUTPUT_LORE = "§7需先在机器里设置对应产物"
"""
产物格的补充说明：同一桶水既可以冻成雪球也可以冻成冰，得**先在机器界面里选定要做哪一种**。
走悬停而不是可见文字：它是补充说明，不是读这条配方必须看到的数。
"""


def Lore(recipe):  # type: (any) -> dict
    """ 产物格的 lore。键是**绑定前缀**（布局表里冷冻机只有一个产物格：output0） """
    _ = recipe
    return {"mei_ui.recipe.output0": OUTPUT_LORE}


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.freezer",
        recipes=recipes,
        sort_index=SORT_INDEX,
        lores=Lore,
    )
