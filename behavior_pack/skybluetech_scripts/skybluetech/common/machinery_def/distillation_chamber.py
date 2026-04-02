# coding=utf-8
from ..define.id_enum import DISTILLATION_CHAMBER
from ..define.id_enum import fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.distillation_chamber import DistillatorChamberRecipe, c2k


recipes = RecipesCollection(
    DISTILLATION_CHAMBER,
    DistillatorChamberRecipe(
        "minecraft:water", 50, fluids.DISTILLED_WATER, 45, c2k(30), c2k(80), c2k(100)
    ),
    DistillatorChamberRecipe(
        fluids.RAW_OIL, 5, fluids.LUBRICANT, 4, c2k(50), c2k(55), c2k(60)
    ),
    DistillatorChamberRecipe(
        fluids.VEGETABLE_OIL, 5, fluids.LUBRICANT, 2, c2k(55), c2k(62), c2k(70)
    ),
)
