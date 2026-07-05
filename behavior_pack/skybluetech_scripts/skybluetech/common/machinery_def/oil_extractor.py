# coding=utf-8
from ..define.id_enum import Machinery, items, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.oil_extractor import MachineRecipe, OilExtractorRecipe

STORE_RF_MAX = 8000
MAX_FLUID_VOLUME = 1000


recipes = RecipesCollection(
    Machinery.OIL_EXTRACTOR,
    OilExtractorRecipe(
        items.SUNFLOWER_SEEDS,
        fluids.CommonOil.VEGETABLE_OIL,
        50,
        tick_duration=60,
        power_cost=40,
    ),
    OilExtractorRecipe(
        "minecraft:wheat_seeds",
        fluids.CommonOil.VEGETABLE_OIL,
        5,
        tick_duration=50,
        power_cost=40,
    ),
)  # type: RecipesCollection[MachineRecipe]
