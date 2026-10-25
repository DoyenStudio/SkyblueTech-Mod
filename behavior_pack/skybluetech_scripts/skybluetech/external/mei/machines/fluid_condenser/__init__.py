# coding=utf-8
"""
流体冷却机（`fluid_condenser`）—— 流体 → 物，**榨油机的镜像**。

接它是为了验反向：此前流体只出现在**产物**侧（榨油机、熔岩炉），
这台第一次把流体格放到**输入**侧。两侧走的是同一个 `FluidPanel`，
差别只有 `input_kind` 一个字符串加布局里那格控件换成 `fluid_slot`。

典型配方：**1000 mB 熔岩 → 黑曜石**（40 RF/t × 100 刻 = 4000 RF，5 秒）。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:fluid_condenser"
RECIPE_CLS = "FluidCondenserRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiFluidCondenser.RECIPES_GRID"
INPUT_CELLS = 1
SORT_INDEX = 112

INPUT_KIND = convert.CATEGORY_FLUID
""" 输入格的条目种类。**写成模块常量而不是直接填参数**：
    离线探针 `probe_skyblue_machines.py` 靠读这些常量来比对
    「声明的格子」与「真实配方槽位」，填成字面量它就看不见 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.fluid_condenser",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        input_kind=INPUT_KIND,
    )
