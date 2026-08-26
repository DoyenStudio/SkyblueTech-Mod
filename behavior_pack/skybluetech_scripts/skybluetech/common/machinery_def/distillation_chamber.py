# coding=utf-8
from ..define.id_enum import Machinery
from ..define.id_enum import fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.distillation_chamber import DistillationChamberRecipe, c2k

K_OUTPUT_RATE = "st:output_rate"
INPUT_MAX_VOLUME = 1500
OUTPUT_MAX_VOLUME = 1500

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
    ),
    DistillationChamberRecipe(
        fluids.CommonOil.RAW_OIL,
        5,
        fluids.CommonOil.LUBRICANT,
        4,
        c2k(50),
        c2k(55),
        c2k(60),
    ),
    DistillationChamberRecipe(
        fluids.CommonOil.VEGETABLE_OIL,
        5,
        fluids.CommonOil.LUBRICANT,
        2,
        c2k(55),
        c2k(62),
        c2k(70),
    ),
)
