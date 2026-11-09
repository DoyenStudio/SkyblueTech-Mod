# coding=utf-8
from ..define.id_enum import Machinery, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.define import CategoryType, Input, Output
from ..mini_jei.machinery.specialized_growth_chamber import SpecializedGrowthChamberRecipe
from .hydroponic_bed import POWER_COST, STORE_RF_MAX
from .specialized_growth_base import FLUID_SLOT_MAX_VOLUMES

recipes = RecipesCollection(
    Machinery.SPECIALIZED_GROWTH_CHAMBER,
    SpecializedGrowthChamberRecipe(
        inputs={
            CategoryType.ITEM: {
                1: Input("minecraft:wither_rose", 0),
                2: Input("minecraft:soul_soil", 0),
            },
            CategoryType.FLUID: {0: Input(fluids.CommonLiquid.EVIL_UNDEAD, 500)},
        },
        outputs={CategoryType.ITEM: {3: Output("minecraft:wither_rose")}},
        tick_duration=25600,
    ),
)
