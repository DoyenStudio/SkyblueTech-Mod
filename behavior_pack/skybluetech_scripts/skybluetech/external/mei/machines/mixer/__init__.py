# coding=utf-8
"""
固液搅拌机（`mixer`）—— 与金属冲压机同形（流体 + 物品 → 物品）。

**多一个看点：4 条配方里有 1 条没有流体**（`input_fluid_id` 是 `None`），
所以同一个配方类型里既有「流 + 物」也有「纯物」。
按 `(种类, 槽位号)` 反查天然处理这件事：那条配方查 `fluid:0` 查不到 ⇒
返回 `None` ⇒ `render_slot` 画一个空的**流体格**，物品那格照常。
**换成按位置取就会翻车** —— 那条配方的 `input_slots` 只有 `["item:0"]`，
按位置第 0 个就是物品，会被画进流体格里。

典型配方：**1 下界岩 + 500 mB 熔岩 → 岩浆块**（40 RF/t × 40 刻 = 1600 RF）。
验空流体格用那条**没有流体**的：左边流体格应当是空的，不是画着别的东西。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:mixer"
RECIPE_CLS = "MixerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiMixer.RECIPES_GRID"
SORT_INDEX = 115

INPUT_SLOTS = ((convert.CATEGORY_FLUID, 0), (convert.CATEGORY_ITEM, 0))
""" 同金属冲压机：第 0 格流体、第 1 格物品，与布局里的 `input` 面板对齐 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.mixer",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        input_slots=INPUT_SLOTS,
    )
