# coding=utf-8
"""
冷冻机（`freezer`）—— 流体 → 物，与流体冷却机**完全同形**。

> 旧结论「`FreezerRecipesCollection.__init__` 收一个 dict，迭代方式要单独确认」
> **已确认，没有活**：`list()` 直接出 5 条，与其他机器无差别
> （2026-09-04 实测，`skybluetech.md` §7.11.2-4）。
> 配方对象上那个 `index` 字段是蔚蓝自己界面用的，MEI 侧一处也用不到。

典型配方：**250 mB 水 → 雪球**（40 RF/t × 20 刻 = 800 RF，1 秒）。
另一条：**1000 mB 水 → 冰**（耗时 400 刻 = 20 秒，正好压在进度条周期上限）。
"""
from .._common import BuildMachine
from ... import convert, exports

CATEGORY_ID = "skybluetech:freezer"
RECIPE_CLS = "FreezerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiFreezer.RECIPES_GRID"
INPUT_CELLS = 1
SORT_INDEX = 113

INPUT_KIND = convert.CATEGORY_FLUID
""" 输入格的条目种类。**写成模块常量而不是直接填参数**：
    离线探针 `probe_skyblue_machines.py` 靠读这些常量来比对
    「声明的格子」与「真实配方槽位」，填成字面量它就看不见 """


OUTPUT_LORE = "§7需先在机器里设置对应产物"
"""
产物格的补充说明（作者提）。

冷冻机不是「放料就出活」—— 同一桶水既可以冻成雪球也可以冻成冰，
得**先在机器界面里选定要做哪一种**。这是读完配方还会踩的坑，
所以写出来，不靠玩家自己发现。

> 走 hover 而不是可见 label：它是**补充说明**，不是「读这条配方
> 必须看到的数」—— 后者才走 `LABELS`（`skybluetech.md` §7.14.5）。
"""


def Lore(recipe):  # type: (any) -> dict
    """ 产物格的 lore。键是**绑定前缀**，与 `LABELS` 的控件路径不同 """
    _ = recipe
    return {"mei_ui.recipe.output": OUTPUT_LORE}


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.freezer",
        control_def=CONTROL_DEF,
        recipes=recipes,
        input_cells=INPUT_CELLS,
        sort_index=SORT_INDEX,
        input_kind=INPUT_KIND,
        lores=Lore,
    )
