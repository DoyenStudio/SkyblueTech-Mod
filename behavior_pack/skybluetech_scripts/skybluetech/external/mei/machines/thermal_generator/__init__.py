# coding=utf-8
"""
火力发电机（`thermal_generator`）—— 燃料 → RF。

配方页照蔚蓝 UI 规范 v2：燃料格 + 火焰 + 能量条（随进度充满），耗时与产能在火焰与能量条的悬停里。布局在 `_layouts.py`。

**数据不是配方集合**：燃料表 `FUEL_TICK_MAP`（物品 id → 燃烧刻数，224 项）+ 功率 `TICK_POWER`。像 MEI 的燃料页那样一样燃料一条
（`runtime.ListRecipeSource`）：只有输入、没有产物，查燃料的用途时出这一页；物品表里没有的燃料跳过。
机器还认引擎给了燃烧时长的别的物品（`fuelDuration > 0`），那些不在表里，这一页不列。
**导出缺口**：表不在 `common.export` 里，经 `exports.InternalModule` 取，见 `skybluetech.md` §8.11。

典型配方：**煤炭 → 50 RF/t × 80 秒**
"""
from .._common import BuildMachine
from ... import exports, runtime

CATEGORY_ID = "skybluetech:thermal_generator"
MACHINE_ID = "skybluetech:thermal_generator"
SORT_INDEX = 123


def Build():  # type: () -> tuple
    module = exports.InternalModule("common.machinery_def.thermal_generator")
    fuels = dict(getattr(module, "FUEL_TICK_MAP", None) or {})
    power = int(getattr(module, "TICK_POWER", 0) or 0)
    if not fuels or power <= 0:
        raise LookupError("火力发电机的燃料表或功率取不到")

    def make():  # type: () -> list
        recipes = []
        for item_id, ticks in sorted(fuels.items()):
            recipe = runtime.MakeRecipe(
                CATEGORY_ID, [("item", 0, item_id, 1, 1)], [],
                {"output_power": power, "tick_duration": int(ticks)})
            if recipe.GetInputs() and recipe.GetInputs()[0].get_stacks():
                recipes.append(recipe)
        return recipes

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=MACHINE_ID,
        name_key="skybluetech.mei.category.thermal_generator",
        sort_index=SORT_INDEX,
        source=runtime.Build().ListRecipeSource(CATEGORY_ID, make),
    )
