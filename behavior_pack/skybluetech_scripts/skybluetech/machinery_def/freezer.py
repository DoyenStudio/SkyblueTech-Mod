# coding=utf-8
#
from ..mini_jei.machines.freezer import *


recipes = {
    0: FreezerRecipe(
        0, 
        "minecraft:water", 250,
        "minecraft:snowball", 1,
        tick_duration=20, power_cost=50
    ),
    1: FreezerRecipe(
        1,
        "minecraft:water", 1000,
        "minecraft:snow", 1,
        tick_duration=80, power_cost=40
    ),
    2: FreezerRecipe(
        2,
       "minecraft:water", 1000,
        "minecraft:ice", 1,
        tick_duration=80, power_cost=50
    ),
    3: FreezerRecipe(
        3,
        "minecraft:water", 1000,
        "minecraft:packed_ice", 1,
        tick_duration=75, power_cost=45
    ),
    4: FreezerRecipe(
        4,
        "minecraft:water", 10000,
        "minecraft:blue_ice", 1,
        tick_duration=400, power_cost=50
    ),
}
