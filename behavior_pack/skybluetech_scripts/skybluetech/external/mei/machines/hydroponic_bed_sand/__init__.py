# coding=utf-8
"""
沙培床。

配方形状是「一粒种子 → 一堆收获」，与另一种水培床相同，共用件在 `_hydroponic.py`。

沙培没有生长阶段（只有 `once_grow_progress`），所以作物模型是静态的。
"""
from .._common import BuildMachine
from ... import exports
from .._hydroponic import BuildUIScript, MakeDecorate

CATEGORY_ID = "skybluetech:hydroponic_bed_sand"
RECIPE_CLS = "HydroponicBedSandRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiHydroponicSand.RECIPES_GRID"
"""
复用土培那份布局，只覆盖 `$shell_texture` —— 两种床唯一的视觉差别就是
作物背后那张床的贴图。minijei 两种床共用了土培那张，这里各用各的。
"""

SORT_INDEX = 106

ANIMATED = False
""" 有没有生长阶段可播。沙培没有 stages，模型停在第 0 阶段 """

RETURN_SEED = False
"""
收获时**返不返还种子**。判据取自服务端 `finish_once`：
土培会 `OutputItem(种子, 随机数量)`，沙培只输出收获物。
"""

_UI_SCRIPT = None


def Build():  # type: () -> tuple
    global _UI_SCRIPT
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    if _UI_SCRIPT is None:
        _UI_SCRIPT = BuildUIScript(CATEGORY_ID, ANIMATED)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.hydroponic_bed_sand",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        # POWER_COST 是**模块级常量**，不在配方对象上，见 _hydroponic.Decorate
        decorate=MakeDecorate(RETURN_SEED, exports.OwnerConstant(recipes, "POWER_COST", 0)),
        ui_script=_UI_SCRIPT,
    )
