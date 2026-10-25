# coding=utf-8
"""
金属冲压机（`metal_press`）—— **首台混合输入**：一格流体 + 一格物品 → 一格物品。

它是「按格 `(种类, 槽位号)` 表」这个改动存在的理由。蔚蓝的槽位号
**按类别分命名空间**，这台的两个输入是 `fluid:0` 与 `item:0` —— **两个 0**。
只按格子下标反查的话，第 1 格会去问 `item:1`，落空成空格，
物品那格永远不出现（`skybluetech.md` §7.11.3）。

产物在 `item:1` 而不是 `item:0` —— 但只有一个产物，所以走
`GetPrimaryOutput()` 那条默认分支就够，不必给 `output_slots`。

典型配方：**1 铜锭 + 10 mB 润滑油 → 2 铜杆**（40 RF/t × 40 刻 = 1600 RF，2 秒）。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:metal_press"
RECIPE_CLS = "MetalPressRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiMetalPress.RECIPES_GRID"
SORT_INDEX = 114

INPUT_SLOTS = ((convert.CATEGORY_FLUID, 0), (convert.CATEGORY_ITEM, 0))
"""
按格的 `(种类, 槽位号)`。**顺序要与布局里 input0 / input1 的控件类型对上** ——
布局里 `input` 面板的第 0 格是流体格、第 1 格是物品格，与这里一致。
两边对不上的表现是「格子画对了但永远空着」，且零报错。
"""


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.metal_press",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        input_slots=INPUT_SLOTS,
    )
