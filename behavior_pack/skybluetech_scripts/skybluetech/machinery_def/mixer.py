# coding=utf-8
#
from ..mini_jei.machines.mixer import *


recipes = [
    MixerRecipe(
        "minecraft:lava", 500,
        "minecraft:netherrack", 1,
        "minecraft:magma", 1,
        tick_duration=80,
        power_cost=40,
    ),
    MixerRecipe(
        "minecraft:water", 400,
        "skybluetech:dust_block", 1,
        "minecraft:clay", 1,
        tick_duration=40,
        power_cost=30,
    ),
] # type: list[MachineRecipe]
