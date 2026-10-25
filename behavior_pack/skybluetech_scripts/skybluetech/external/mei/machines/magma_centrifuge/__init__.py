# coding=utf-8
"""
高热流体离心机（`magma_centrifuge`）—— **首台多产物**：一路流体分成最多四路。

两件与别台不同的事：

  1. **产物槽位从 1 起编号**（`fluid:1~6`，`fluid:0` 是输入那一格）。
     所以必须给 `output_slots` 把真实槽号写出来，
     不能让格子下标去当槽位号 —— 那样第 0 格会去问 `fluid:0`，
     拿到的是**输入**那一格的东西。
  2. **首台真正用上液面分母**：一次出 18/60/18/4 mB，不按同方向最大体积
     归一的话几格全满，"谁多谁少"就看不出来了。归一逻辑在
     `_common.MachineUIScript.CacheMaxVolume`，本模块不用管。

> 布局排**六格**（同机器本体与 minijei），而当前数据最多只用到 4 路
> （4 条配方里 3 条是 4 出、1 条是 3 出）。用不到的格渲染成空流体格，是对的。

典型配方：**100 mB 熔岩 → 18 轻质熔岩 + 60 中质熔岩 + 18 重质熔岩 + 4 熔融土**
（80 RF/t × 100 刻 = 8000 RF，5 秒）。前四格液面高度应当明显不同，后两格空着。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:magma_centrifuge"
RECIPE_CLS = "MagmaCentrifugeRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiMagmaCentrifuge.RECIPES_GRID"
SORT_INDEX = 116

FLUID = convert.CATEGORY_FLUID
INPUT_SLOTS = ((FLUID, 0),)
OUTPUT_SLOTS = tuple((FLUID, i) for i in range(1, 7))
"""
产物槽位号 **1~6**，与布局里 output0~5 六个格子一一对应。

**格数跟机器走，不跟当前数据走**：机器本体就是六个产出口
（`MagmaCentrifugeUI` 的 `right_fluid1..6`），minijei 的配方布局也排了六格。
当前四条配方最多只用到 4 路 —— 那两格会渲染成空的流体格，
但蔚蓝以后加一条 5/6 产物的配方时**这里不用改**。

> 我上一轮按"实测最多 4 路"砍到四格，是拿**当前数据**当机器能力了
> （2026-09-04 作者纠正）。同类判断在工业研究上也犯过一次：
> 数据最多 7 格而机器是 3×3。
"""


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.magma_centrifuge",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        input_slots=INPUT_SLOTS,
        output_slots=OUTPUT_SLOTS,
    )
