# coding=utf-8
from ..mini_jei.machinery.hydroponic_bed import (
    HydroponicBedRecipe,
    HydroponicBedRecipesCollection,
    Output,
)

K_GROW_STAGE = "st:grow_stage"
K_STAGE_GROW_TICKS = "st:stage_grow_ticks"
K_WATER_STORE = "st:water_store"
K_CROP_ID = "st:crop_id"
WORK_TICK_DELAY = 5
POWER_COST = 4
ONCE_WATER_COST = 5
MAX_WATER_STORE = 1000


recipes = HydroponicBedRecipesCollection({
    "minecraft:wheat_seeds": HydroponicBedRecipe(
        "minecraft:wheat",
        "minecraft:wheat_seeds",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [Output("minecraft:wheat")],
    ),
    "minecraft:carrot": HydroponicBedRecipe(
        "minecraft:carrots",
        "minecraft:carrot",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [],
    ),
    "minecraft:potato": HydroponicBedRecipe(
        "minecraft:potatoes",
        "minecraft:potato",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [],
    ),
    "minecraft:beetroot_seeds": HydroponicBedRecipe(
        "minecraft:beetroot",
        "minecraft:beetroot_seeds",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [Output("minecraft:beetroot")],
    ),
})
