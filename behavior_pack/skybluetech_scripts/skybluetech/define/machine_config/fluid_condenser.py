# coding=utf-8
#
from ...mini_jei.machines.fluid_condenser import *


recipes = [
    FluidCondenserRecipe(
        "minecraft:lava", 1000,
        "minecraft:obsidian", 1,
        tick_duration=200, power_cost=50
    ),
    #
    recipeMolten2Ingot("copper"),
    recipeMolten2Ingot("iron"),
    recipeMolten2Ingot("gold"),
    recipeMolten2Ingot("tin"),
    recipeMolten2Ingot("lead"),
    recipeMolten2Ingot("silver"),
    recipeMolten2Ingot("platinum"),
    recipeMolten2Ingot("nickel"),
]
