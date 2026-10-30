# coding=utf-8
"""
合金炉（`alloy_furnace`）—— 2×2 进 1 出。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/AlloyFurnace.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 机器新界面是 2×2 输入、火焰在箭头正上方。第 3 号槽常放**热源**（烈焰粉、惰性红石，4 条配方），
> 不是第四样合金材料（照 minijei 查过，`skybluetech.md` §7.14）。
> 槽位是**稀疏**的（8 条配方只用 0 与 2），格子与材料按真实槽位号对应（`IngredientForCell`）。
> 5 号产出格 20 条配方都不用，照机器预留（配方没用到的格子也画出来）。
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
