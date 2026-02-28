# coding=utf-8
#
from ...common.define.id_enum import items, fluids
from ..mini_jei.machinery.oil_extractor import MachineRecipe, OilExtractorRecipe


recipes = [
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
]  # type: list[MachineRecipe]
