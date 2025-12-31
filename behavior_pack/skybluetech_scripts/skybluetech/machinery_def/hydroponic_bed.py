# coding=utf-8

from ..mini_jei.machines.hydroponic_bed import *


recipes = {
    "minecraft:wheat_seeds": HydroponicBedRecipe(
        "minecraft:wheat",
        "minecraft:wheat_seeds",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [Output("minecraft:wheat")]
    ),
    "minecraft:carrot": HydroponicBedRecipe(
        "minecraft:carrots",
        "minecraft:carrot",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        []
    ),
    "minecraft:potato": HydroponicBedRecipe(
        "minecraft:potatoes",
        "minecraft:potato",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        []
    ),
    "minecraft:beetroot_seeds": HydroponicBedRecipe(
        "minecraft:beetroot",
        "minecraft:beetroot_seeds",
        100,
        8,
        [0.1016, 0.3484, 0.3982, 0.1517],
        [Output("minecraft:beetroot")]
    ),
}
