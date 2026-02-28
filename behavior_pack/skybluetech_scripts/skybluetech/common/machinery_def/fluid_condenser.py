# coding=utf-8
#
from ..mini_jei.machinery.fluid_condenser import (
    FluidCondenserRecipe,
    MachineRecipe,
    recipe_molten2ingot,
)


recipes = [
    FluidCondenserRecipe(
        "minecraft:lava",
        1000,
        "minecraft:obsidian",
        1,
        tick_duration=200,
        power_cost=50,
    ),
    #
    recipe_molten2ingot("copper"),
    recipe_molten2ingot("iron"),
    recipe_molten2ingot("gold"),
    recipe_molten2ingot("tin"),
    recipe_molten2ingot("lead"),
    recipe_molten2ingot("silver"),
    recipe_molten2ingot("platinum"),
    recipe_molten2ingot("nickel"),
]  # type: list[MachineRecipe]
