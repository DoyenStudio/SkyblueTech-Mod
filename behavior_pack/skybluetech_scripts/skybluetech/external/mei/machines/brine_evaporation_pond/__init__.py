# coding=utf-8
"""
卤水池（`brine_evaporation_pond`，多方块结构）—— 流体 → 流体，连续蒸发、不耗电、要热。

配方页照蔚蓝 UI 规范 v2：左边的温度计是池子当前的温度（机器状态），不画；
配方要求的温度与耗热写进箭头的悬停。布局在 `_layouts.py`。

**导出缺口**：配方类 `BrineEvaporationPondRecipe` 还没进 `common.export.recipes` ⇒ 先按集合名（控制器的方块 id）取，
导出补上之后 `exports.Collection` 那条自动接上。见 `skybluetech.md` §8.11。

典型配方：**25 mB 稀卤水 → 10 mB 饱和卤水**（≥ 350 K，最适 360 K）
"""
from .._common import BuildMachine, Kelvin
from ... import exports

CATEGORY_ID = "skybluetech:brine_evaporation_pond"
RECIPE_CLS = "BrineEvaporationPondRecipe"
CONTROLLER = "skybluetech:brine_evaporation_pond_controller"
""" 控制器方块（= 配方集合名 = 配方类的 recipe_icon_id）。方块 id 是公开的，写死它比碰内部模块稳 """

SORT_INDEX = 129


def _Collection():  # type: () -> tuple
    try:
        return exports.Collection(RECIPE_CLS)
    except LookupError:
        return CONTROLLER, exports.NamedCollection(CONTROLLER)


def Build():  # type: () -> tuple
    icon_id, recipes = _Collection()

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.brine_evaporation_pond",
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=_Decorate,
    )


def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    data = parts["data"]
    conditions = []
    fit = getattr(sb_recipe, "fit_temperature", None)
    low = getattr(sb_recipe, "min_temperature", None)
    heat = getattr(sb_recipe, "heat_cost", None)
    if fit is not None:
        conditions.append("§7最适温度： §f" + Kelvin(fit))
    if low is not None:
        conditions.append("§7最低温度： §f" + Kelvin(low))
    if heat:
        conditions.append("§7最适温度下每次耗热： §f%s RF" % _Number(heat))
    data["conditions"] = conditions


def _Number(value):  # type: (float) -> str
    value = float(value)
    return "%d" % int(value) if value == int(value) else "%.1f" % value
