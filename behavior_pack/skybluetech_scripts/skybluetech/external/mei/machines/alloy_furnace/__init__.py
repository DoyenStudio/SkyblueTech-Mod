# coding=utf-8
"""
合金炉（`alloy_furnace`）—— 2×2 无序输入，有序输出。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/AlloyFurnace.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
材料允许放入 0～3 任意输入槽，内置配方的产物固定放入槽 4。
输入展示按条目顺序填槽，输出展示使用配方指定的槽位。
典型配方：**3 铝锭 + 2 钛锭 + 铁锭 → 3 铝钛合金锭**
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:alloy_furnace"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "AlloyFurnaceRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 102


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.alloy_furnace",
        recipes=recipes,
        sort_index=SORT_INDEX,
    )
