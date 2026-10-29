# coding=utf-8
"""
小型蒸馏仓（`distillation_chamber`）—— 流体 → 流体（连续过程，不耗电）。

配方页照蔚蓝 UI 规范 v2：格子顺序、能量条、进度都在 `_layouts.py`（生成器从机器界面算出，
与 `ui/mei_recipes/DistillationChamber.json` 同一次生成），`BuildMachine` 自动取 —— 本模块只声明身份。
> 机器右边的温度数据板不画（规范 v2 §12.5）：最适温度、温度范围进箭头的悬停（`Data["conditions"]`）。
典型配方：**50 mB 水 → 45 mB 蒸馏水**
"""
from .._common import BuildMachine
from ... import exports
from .._common import Kelvin

CATEGORY_ID = "skybluetech:distillation_chamber"
""" MEI 的配方类型标识。**带命名空间** —— 类型 id 在 MEI 里全局唯一，不带前缀迟早和别的模组撞上 """

RECIPE_CLS = "DistillationChamberRecipe"
""" 蔚蓝导出（common.export.recipes）里的配方类名；机器 id 与配方集合都由它取 """

SORT_INDEX = 117

TEMPERATURE_FIELDS = ("min_temperature", "max_temperature", "fit_temperature")
""" 搬进 `Recipe.Data` 的温度字段（标量，Data 会随配方序列化出去） """


def Decorate(sb_recipe, parts):  # type: (any, dict) -> None
    """ 温度在配方对象的属性上，不在 inputs/outputs 里：搬进 Data，再写成悬停的条件行 """
    data = parts["data"]
    for name in TEMPERATURE_FIELDS:
        value = getattr(sb_recipe, name, None)
        if value is not None:
            data[name] = int(value)
    conditions = []
    if data.get("fit_temperature") is not None:
        conditions.append("§7最适温度： §f" + Kelvin(data["fit_temperature"]))
    if data.get("min_temperature") is not None and data.get("max_temperature") is not None:
        conditions.append("§7温度范围： §f%d ~ %d K" % (data["min_temperature"], data["max_temperature"]))
    data["conditions"] = conditions


def Build():  # type: () -> tuple
    icon_id, recipes = exports.Collection(RECIPE_CLS)

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=icon_id,
        name_key="skybluetech.mei.category.distillation_chamber",
        recipes=recipes,
        sort_index=SORT_INDEX,
        decorate=Decorate,
    )
