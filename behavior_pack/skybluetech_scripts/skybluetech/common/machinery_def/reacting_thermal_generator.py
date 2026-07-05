# coding=utf-8
from ..define.id_enum import Machinery, items, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.reacting_thermal_generator import (
    GeneratorRecipe,  # noqa: F401
    ReactingThermalGeneratorRecipe,
)

STORE_RF_MAX = 14400
MAX_FLUID_VOLUMES = (1000, 1000)

recipes = RecipesCollection(
    Machinery.REACTING_THERMAL_GENERATOR,
    ReactingThermalGeneratorRecipe(
        items.SULFUR, "minecraft:water", 250, fluids.Acid.SULFURIC_ACID, 250, 45, 800
    ),
    ReactingThermalGeneratorRecipe(
        items.Dusts.SULFUR,
        "minecraft:water",
        250,
        fluids.Acid.SULFURIC_ACID,
        250,
        64,
        600,
    ),
)  # type: RecipesCollection[GeneratorRecipe]
