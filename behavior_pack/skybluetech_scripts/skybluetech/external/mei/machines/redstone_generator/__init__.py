# coding=utf-8
"""
红石发电机（`redstone_generator`）—— 物 → 物 + RF。

**RF 怎么显示**：照 minijei 的 `GeneratorRecipeRenderer` ——
`output_power` 写**一次运行的总量**、`tick_power` 写**功率**，
两个都是可见 label，**布局里没有电力条**。
（电力条是给耗电机器的；发电机套一根反向的条既不像 minijei，
数字还得 hover 才看得到。）

RF 的来源有两条路，都通，所以数据侧零新代码：
  · `GeneratorRecipe.__init__` 自己往 outputs 里注了一格 `energy:0`
    （`mini_jei/machinery/define.py:74`）⇒ 落进 `Data["extra_outputs"]`；
  · `output_power` 也在属性上 ⇒ 被 `runtime._Convert` 抓进 `Data`。
`GeneratorLabels` 读的是后者。

产物 `item:1` 只有一个 ⇒ 走 `GetPrimaryOutput()` 默认分支，不必给 `output_slots`。
`energy` 不做成槽位：它没有身份、不进物品表、点了查不出用途。

典型配方：**红石 → 失活红石**（产 160 RF/t × 10 刻 = 1600 RF）。
右侧应显示「1.6k RF」与「160 RF/t」两行，输入格下方有一簇火焰。
"""
from .._common import BuildMachine, GeneratorLabels
from ... import exports

CATEGORY_ID = "skybluetech:redstone_generator"
RECIPE_CLS = "RedstoneGeneratorRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiRedstoneGenerator.RECIPES_GRID"
INPUT_CELLS = 1
SORT_INDEX = 120


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.redstone_generator",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        # RF 两个数直推成可见文字（照 minijei），不用电力条
        labels=GeneratorLabels,
    )
