# coding=utf-8
"""
熔岩炉（`magma_furnace`）—— 物 → 流体，与榨油机同形。

**这台的看点是标签**：20 条配方里有 **10 条的输入是 tag**
（`raws/tin` / `ingots/tin` …），是全项目第一台会大量出现
`MultiItemPanel` 轮播的机器。此前轮播只在原版熔炉的燃料格上验过。
标签成员是异步到的，转换走 `Ingredient.from_tag` 而不是字面展开
（否则「扫到一半」与「扫完」会算出两个 `Recipe.Id`，见 convert.to_ingredient）。

典型配方：**岩浆块 → 1000 mB 熔岩**（50 RF/t × 100 刻 = 5000 RF，5 秒）。
另一条看轮播：**锡矿石标签 `raws/tin` → 熔融锡** —— 那一格应当在
若干候选矿石之间轮播，而不是只显示一个。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:magma_furnace"
RECIPE_CLS = "MagmaFurnaceRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiMagmaFurnace.RECIPES_GRID"
INPUT_CELLS = 1
SORT_INDEX = 111


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.magma_furnace",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        # 产物是流体 ⇒ 走 FluidPanel；布局那边把产物格换成 output_fluid
        output_kind=convert.CATEGORY_FLUID,
    )
