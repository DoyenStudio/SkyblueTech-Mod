# coding=utf-8
from ..define.id_enum import METAL_PRESS, Ingots, Sticks
from ..define.id_enum.fluids import LUBRICANT
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.metal_press import MachineRecipe, MetalPressRecipe


recipes = RecipesCollection(
    METAL_PRESS,
    MetalPressRecipe(
        LUBRICANT,
        10,
        "minecraft:copper_ingot",
        1,
        Sticks.COPPER,
        2,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.TIN,
        1,
        Sticks.TIN,
        2,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.SILVER,
        1,
        Sticks.SILVER,
        2,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.PLATINUM,
        1,
        Sticks.PLATINUM,
        2,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.STEEL,
        1,
        Sticks.STEEL,
        2,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.BRONZE,
        1,
        Sticks.BRONZE,
        2,
        tick_duration=60,
        power_cost=50,
    ),
)  # type: RecipesCollection[MachineRecipe]
