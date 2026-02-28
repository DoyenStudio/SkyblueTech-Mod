# coding=utf-8
#
from ...common.define.id_enum.items import Ingots, Sticks
from ...common.define.id_enum.fluids import LUBRICANT
from ..mini_jei.machinery.metal_press import MetalPressRecipe, MachineRecipe


recipes = [
    MetalPressRecipe(
        LUBRICANT,
        10,
        "minecraft:copper_ingot",
        1,
        Sticks.COPPER,
        1,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.TIN,
        1,
        Sticks.TIN,
        1,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.SILVER,
        1,
        Sticks.SILVER,
        1,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.PLATINUM,
        1,
        Sticks.PLATINUM,
        1,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.STEEL,
        1,
        Sticks.STEEL,
        1,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        LUBRICANT,
        10,
        Ingots.BRONZE,
        1,
        Sticks.BRONZE,
        1,
        tick_duration=60,
        power_cost=50,
    ),
]  # type: list[MachineRecipe]
