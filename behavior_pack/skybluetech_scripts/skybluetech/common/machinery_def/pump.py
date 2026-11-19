# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import Machinery, fluids
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.pump import PumpRecipe

K_CACHED_VOLUME = "st:cached_volume"
K_CACHED_FLUID_ID = "st:cached_fluid_id"

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 4000

recipes = RecipesCollection(
    Machinery.PUMP,
    PumpRecipe(fluids.Vanilla.WATER),
    PumpRecipe(fluids.Vanilla.LAVA),
)
