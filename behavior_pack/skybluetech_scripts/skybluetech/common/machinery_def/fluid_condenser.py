# coding=utf-8
from ..define.id_enum import FLUID_CONDENSER, Molten
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.fluid_condenser import (
    FluidCondenserRecipe,
    recipe_molten2ingot,
)


recipes = RecipesCollection(
    FLUID_CONDENSER,
    FluidCondenserRecipe(
        "minecraft:lava",
        1000,
        "minecraft:obsidian",
        1,
        tick_duration=200,
        power_cost=50,
    ),
    FluidCondenserRecipe(
        Molten.EARTH,
        1000,
        "minecraft:cobblestone",
        1,
        tick_duration=100,
        power_cost=40,
    ),
    recipe_molten2ingot("copper"),
    recipe_molten2ingot("iron"),
    recipe_molten2ingot("gold"),
    recipe_molten2ingot("tin"),
    recipe_molten2ingot("lead"),
    recipe_molten2ingot("silver"),
    recipe_molten2ingot("platinum"),
    recipe_molten2ingot("nickel"),
)
