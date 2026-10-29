# coding=utf-8
"""
地热发电机（`geothermal_generator`）—— 熔岩（+ 水）→ RF + 黑曜石粉（10%）。

配方页照蔚蓝 UI 规范 v2：两个流体槽 + 火焰 + 能量条 + 产出格。布局在 `_layouts.py`。

**没有配方表，只有常量**（`common.machinery_def.geothermal_generator`）：每次烧 `ONCE_LAVA_REDUCE_VOLUME` 熔岩、
持续 `ONCE_BURNING_TICKS` 刻，带水（`ONCE_WATER_REDUCE_VOLUME`）功率从 `ORIGIN_GENERATED_POWER` 升到
`GENERATED_POWER_WITH_WATER`；每次 10% 出一个黑曜石粉（服务端 `random() > 0.9`）。⇒ 拼成两条固定的配方。
**导出缺口**：常量不在 `common.export` 里，经 `exports.InternalModule` 取，见 `skybluetech.md` §8.11。

典型配方：**200 mB 熔岩 + 400 mB 水 → 320 RF/t × 5 秒 + 黑曜石粉（10%）**；只烧熔岩是 240 RF/t
"""
from .._common import BuildMachine
from ... import exports, runtime

CATEGORY_ID = "skybluetech:geothermal_generator"
MACHINE_ID = "skybluetech:geothermal_generator"
OBSIDIAN_DUST = "skybluetech:obsidian_dust"
""" 副产物（蔚蓝 `id_enum.Dusts.OBSIDIAN`）。物品 id 是公开的 """
BYPRODUCT_CHANCE = 0.1
SORT_INDEX = 124


def Build():  # type: () -> tuple
    module = exports.InternalModule("common.machinery_def.geothermal_generator")
    lava = getattr(module, "LAVA_ID", "minecraft:lava")
    water = getattr(module, "WATER_ID", "minecraft:water")
    lava_volume = getattr(module, "ONCE_LAVA_REDUCE_VOLUME", None)
    water_volume = getattr(module, "ONCE_WATER_REDUCE_VOLUME", None)
    ticks = getattr(module, "ONCE_BURNING_TICKS", None)
    power = getattr(module, "ORIGIN_GENERATED_POWER", None)
    power_water = getattr(module, "GENERATED_POWER_WITH_WATER", None)
    if None in (lava_volume, water_volume, ticks, power, power_water):
        raise LookupError("地热发电机的常量取不全")
    byproduct = [("item", 0, OBSIDIAN_DUST, 1, BYPRODUCT_CHANCE)]

    def make():  # type: () -> list
        return [
            runtime.MakeRecipe(CATEGORY_ID, [("fluid", 0, lava, lava_volume, 1)], byproduct,
                               {"output_power": int(power), "tick_duration": int(ticks)}),
            runtime.MakeRecipe(CATEGORY_ID, [("fluid", 0, lava, lava_volume, 1), ("fluid", 1, water, water_volume, 1)],
                               byproduct, {"output_power": int(power_water), "tick_duration": int(ticks)}),
        ]

    return BuildMachine(
        category_id=CATEGORY_ID,
        icon_id=MACHINE_ID,
        name_key="skybluetech.mei.category.geothermal_generator",
        sort_index=SORT_INDEX,
        source=runtime.Build().ListRecipeSource(CATEGORY_ID, make),
    )
