# coding=utf-8
"""
热力反应发电机（`reacting_thermal_generator`）—— 这批里最复杂的一台：
**混合输入 + 产电 + 流体产物**（流体 + 物 → 流体 + RF）。

三样东西同时出现，但每一样都已经在别处解决过，所以这台仍然是纯参数：
  · 混合输入 → `input_slots` 按格表（同金属冲压机）
  · 产电 → `labels=GeneratorLabels`，RF 两行数字在最右（照 minijei，无电力条）
  · 流体产物 → `output_kind=fluid`

产物 `fluid:1` 只有一格（`energy:0` 不是槽位），走 `GetPrimaryOutput()`。

典型配方：**硫磺 + 250 mB 水 → 250 mB 硫酸**，产 30 RF/t × 800 刻 = 24k RF。
这一行的看点是**四样东西同时对**：左边两格（水 + 硫磺）、中间流体产物（硫酸）、
最右「24.0k RF」与「30 RF/t」两行。
"""
from .._common import BuildMachine, GeneratorLabels
from ... import convert, exports

CATEGORY_ID = "skybluetech:reacting_thermal_generator"
RECIPE_CLS = "ReactingThermalGeneratorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiReactingThermalGenerator.RECIPES_GRID"
SORT_INDEX = 122

INPUT_SLOTS = ((convert.CATEGORY_FLUID, 0), (convert.CATEGORY_ITEM, 0))
""" 与 布局里的 `input` 面板 对齐：第 0 格流体、第 1 格物品 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.reacting_thermal_generator",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        input_slots=INPUT_SLOTS,
        output_kind=convert.CATEGORY_FLUID,
        # RF 两个数直推成可见文字（照 minijei），不用电力条
        labels=GeneratorLabels,
    )
