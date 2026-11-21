# coding=utf-8
from ..define.id_enum import CommonLiquid, Machinery, Molten, HotFluid, HDPE_NUGGET, RESIN, ROSIN
from ..define.resin import RESIN_FLUID_VOLUME
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.fluid_condenser import (
    MachineRecipe,
    FluidCondenserRecipe,
    recipe_molten2ingot,
)

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 1000


recipes = RecipesCollection(
    Machinery.FLUID_CONDENSER,
    FluidCondenserRecipe(HotFluid.MOLTEN_POLYETHYLENE, 144, HDPE_NUGGET, 9, tick_duration=100, power_cost=40),
    FluidCondenserRecipe(Molten.ROSIN, 144, ROSIN, 1, tick_duration=100, power_cost=40),
    FluidCondenserRecipe(
        CommonLiquid.LIQUID_RESIN,
        RESIN_FLUID_VOLUME,
        RESIN,
        1,
        tick_duration=80,
        power_cost=20,
    ),
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
    recipe_molten2ingot("palladium"),
    recipe_molten2ingot("nickel"),
)  # type: RecipesCollection[MachineRecipe]
