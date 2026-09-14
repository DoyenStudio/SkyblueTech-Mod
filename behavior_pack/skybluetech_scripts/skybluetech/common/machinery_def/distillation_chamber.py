# coding=utf-8
from ..define.id_enum import Machinery
from ..define.id_enum import fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.distillation_chamber import DistillationChamberRecipe, c2k

K_OUTPUT_RATE = "st:output_rate"
INPUT_MAX_VOLUME = 1500
OUTPUT_MAX_VOLUME = 1500

CHAMBER_HEAT_CAPACITY = 50.0
# 蒸馏仓的热容, 单位 RF/K, 只影响本机(见 `HeatCtrl.heat_capacity`)。

# 仓里装的是待蒸馏的物料, 当成一大团热容很高的物质: 温度每变动 1K 都要挪 50 RF 热量。
# 不这么做的话, "每产 1 mB 扣 heat_per_produce RF 热"那笔账会一次性把仓温踹下去(热容
# 1.0 时满速一 tick 就扣 100 RF, 等于瞬间掉 100K), 仓温在 240~335K 之间锯齿, 大半时间
# 泡在环境温度以下且不产油。


recipes = RecipesCollection(
    Machinery.DISTILLATION_CHAMBER,
    DistillationChamberRecipe(
        "minecraft:water",
        50,
        fluids.CommonLiquid.DISTILLED_WATER,
        45,
        c2k(30),
        c2k(80),
        c2k(100),
        heat_per_produce=80,
    ),
    DistillationChamberRecipe(
        fluids.CommonOil.RAW_OIL,
        5,
        fluids.CommonOil.LUBRICANT,
        4,
        c2k(50),
        c2k(55),
        c2k(60),
        heat_per_produce=40,
    ),
    DistillationChamberRecipe(
        fluids.CommonOil.VEGETABLE_OIL,
        5,
        fluids.CommonOil.LUBRICANT,
        2,
        c2k(55),
        c2k(62),
        c2k(70),
        heat_per_produce=40,
    ),
)
