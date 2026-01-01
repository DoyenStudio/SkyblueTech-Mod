# coding=utf-8
#
from ..define.id_enum.items import *
from ..define.id_enum.fluids import *
from ..mini_jei.machines.metal_press import *


recipes = [
    MetalPressRecipe(
        LUBRICANT, 10,
        "minecraft:copper_ingot", 1,
        Sticks.COPPER, 1,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT, 10,
        Ingots.TIN, 1,
        Sticks.TIN, 1,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT, 10,
        Ingots.SILVER, 1,
        Sticks.SILVER, 1,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT, 10,
        Ingots.PLATINUM, 1,
        Sticks.PLATINUM, 1,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT, 10,
        Ingots.STEEL, 1,
        Sticks.STEEL, 1,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        LUBRICANT, 10,
        Ingots.BRONZE, 1,
        Sticks.BRONZE, 1,
        tick_duration=60,
        power_cost=50,
    ),
] # type: list[MachineRecipe]
