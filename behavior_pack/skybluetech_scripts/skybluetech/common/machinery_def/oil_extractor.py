# coding=utf-8
from ..define.id_enum import OIL_EXTRACTOR, items, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.oil_extractor import OilExtractorRecipe


recipes = RecipesCollection(
    OIL_EXTRACTOR,
    OilExtractorRecipe(
        items.SUNFLOWER_SEEDS,
        fluids.VEGETABLE_OIL,
        50,
        tick_duration=60,
        power_cost=40,
    ),
    OilExtractorRecipe(
        "minecraft:wheat_seeds",
        fluids.VEGETABLE_OIL,
        5,
        tick_duration=50,
        power_cost=40,
    ),
)
