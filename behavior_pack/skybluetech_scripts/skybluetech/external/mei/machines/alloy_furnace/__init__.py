# coding=utf-8
"""
合金炉。

一台「N 进 1 出」的机器要的东西全在 `_machine.BuildMachine` 里，
本模块只声明它的身份参数。加一台机器就照抄本文件。
"""
from .._common import BuildMachine
from ... import exports

CATEGORY_ID = "skybluetech:alloy_furnace"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，
    不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "AlloyFurnaceRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiAlloyFurnace.RECIPES_GRID"
""" 配方页控件定义名。对应 resource_pack/ui/mei_recipes/AlloyFurnace.json """

INPUT_CELLS = 4
"""
**3 格材料 + 1 格燃料**，不是 4 格材料。

第 3 号槽是**燃料格** —— minijei 的 `alloy_furnace_recipes` 把 slot0/1/2
横排在上、slot3 摆在正中列的**正下方**，中间夹一个 `Flame`，
与原版熔炉同构（`RecipeCheckerLib.json`）。数据也对得上：
用到它的 4 条配方放的是**烈焰粉**与**惰性红石**，都是热源而非合金成分。

> 2026-09-04 的教训：这一格原本压根没画出来（布局只有 3 格），
> 探针扫出来之后我**照数据推**，排成了 2×2 的第 4 格 ——
> 位置对了语义错了，看着像"这条合金配方要四样材料"。
> **应该先去看 minijei 怎么排的。** 见 `skybluetech.md` §7.14。

槽位仍然是**稀疏**的（8 条配方只用 0 与 2），所以格子与材料必须按
真实槽位号对应，不能按列表位置 —— `IngredientForCell` 干的就是这件事。
"""


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.alloy_furnace",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=102,
    )
