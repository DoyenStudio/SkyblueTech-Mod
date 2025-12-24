# coding=utf-8
#
from ..mini_jei.machines.metal_press import *


recipes = [
    MetalPressRecipe(
        "skybluetech:lubricant", 500,
        "minecraft:netherrack", 1,
        "minecraft:magma", 1,
        tick_duration=80,
        power_cost=40,
    ),
] # type: list[MachineRecipe]
