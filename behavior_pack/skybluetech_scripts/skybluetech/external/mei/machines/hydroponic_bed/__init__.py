# coding=utf-8
"""
水培床。

配方形状是「一粒种子 → 一堆收获」，与另一种水培床相同，共用件在 `_hydroponic.py`。

⚠ 配方表是 `HydroponicBedRecipesCollection({...})` —— **dict 不是 varargs**，
但 `RecipesCollection` 内部按 `.values()` 展开，迭代顺序即 dict 顺序。
py2 的 dict 无序 ⇒ **顺序不可依赖**，好在 `Recipe.Id` 只看内容不看顺序，不受影响。
"""
from .._common import BuildMachine
from ... import exports
from .._hydroponic import BuildUIScript, MakeDecorate

CATEGORY_ID = "skybluetech:hydroponic_bed"
RECIPE_CLS = "HydroponicBedRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

CONTROL_DEF = "SkyblueMeiHydroponic.RECIPES_GRID"
""" 两种水培床**共用同一份布局** —— 界面完全一样，只是有没有生长动画之别 """

SORT_INDEX = 105

ANIMATED = True
""" 有没有生长阶段可播。土培有 8 个生长阶段，作物模型按阶段轮播 """

RETURN_SEED = True
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
        name_key="skybluetech.mei.category.hydroponic_bed",
        control_def=CONTROL_DEF,
        recipes=recipes,
        sort_index=SORT_INDEX,
        # POWER_COST 是**模块级常量**，不在配方对象上，见 _hydroponic.Decorate
        decorate=MakeDecorate(RETURN_SEED, exports.OwnerConstant(recipes, "POWER_COST", 0)),
        ui_script=_UI_SCRIPT,
    )
