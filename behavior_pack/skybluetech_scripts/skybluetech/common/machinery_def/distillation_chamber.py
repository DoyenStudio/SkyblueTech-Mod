# coding=utf-8
from ...common.define.id_enum import (
    DISTILLED_WATER,
    RAW_OIL,
    LUBRICANT,
    DISTILLATION_CHAMBER,
)
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.distillation_chamber import DistillatorChamberRecipe, c2k


recipes = RecipesCollection(
    DISTILLATION_CHAMBER,
    DistillatorChamberRecipe(
        "minecraft:water", 50, DISTILLED_WATER, 45, c2k(30), c2k(80), c2k(100)
    ),
    DistillatorChamberRecipe(RAW_OIL, 5, LUBRICANT, 4, c2k(50), c2k(55), c2k(60)),
)
