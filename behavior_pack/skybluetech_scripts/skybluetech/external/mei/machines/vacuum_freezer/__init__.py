# coding=utf-8
"""
真空冷却仓（`vacuum_freezer`）—— 流体 → 流体 / 物（看温度）。

配方页照蔚蓝 UI 规范 v2：机器是 L 档，配方部件只占上两行 ⇒ S 行，主体在行里纵向居中；
上路的输入槽这几条配方都不用，但双路管道通着它，照画成空格。布局在 `_layouts.py`。

  · **配方取全表**：蔚蓝的配方集合只登记了不要升级的两条，要装特化升级的那条（氮气）在同一个模块的 `ALL_RECIPES` 里，
    顺着集合找到（`exports.OwnerConstant`）；要装的升级写进进度的悬停。
  · 配方功率是 0：耗电看机器里设定的温度，能量条照画、悬停写「随设定温度」。

典型配方：**16 mB 压缩空气 → 1 mB 液态空气**（≤ 100 K）；另有 1000 mB 水 → 冰、24 mB 压缩空气 → 1 mB 氮气（要装特化升级）。
"""
from .._common import BuildMachine, Kelvin
from ... import exports

CATEGORY_ID = "skybluetech:vacuum_freezer"
RECIPE_CLS = "VacuumFreezerRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 127

POWER_NOTE = "随机器里设定的温度"
UPGRADER_NAMES = {"skybluetech:upgrader_spec_nitrogen_ext": "特化升级： 氮膜分离"}
""" 要装的升级的名字（同蔚蓝语言文件）；没登记的写「额外的特化升级」 """


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)
    every = exports.OwnerConstant(recipes, "ALL_RECIPES", None)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.vacuum_freezer",
        recipes=list(every) if every else recipes,
        sort_index=SORT_INDEX,
        decorate=_Decorate,
    )


def _Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    data = parts["data"]
    data["power_note"] = POWER_NOTE
    conditions = []
    high = getattr(sb_recipe, "max_temperature", None)
    fit = getattr(sb_recipe, "fit_temperature", None)
    if high is not None:
        conditions.append("§7温度： §f≤ " + Kelvin(high))
    if fit is not None:
        conditions.append("§7最适温度： §f" + Kelvin(fit))
    upgrader = getattr(sb_recipe, "extra_upgrader_id", None)
    if upgrader:
        conditions.append("§7需要装： §f" + UPGRADER_NAMES.get(upgrader, "额外的特化升级"))
    data["conditions"] = conditions
