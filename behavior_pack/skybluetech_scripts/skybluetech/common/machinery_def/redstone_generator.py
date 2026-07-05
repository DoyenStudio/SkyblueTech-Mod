# coding=utf-8
from ..define.id_enum import Machinery, DEACTIVATION_REDSTONE
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.redstone_generator import (
    RedstoneGeneratorRecipe,
    GeneratorRecipe,
)

STORE_RF_MAX = 14400

recipes = RecipesCollection(
    Machinery.REDSTONE_GENERATOR,
    RedstoneGeneratorRecipe("minecraft:redstone", DEACTIVATION_REDSTONE, 1, 160, 10),
    RedstoneGeneratorRecipe(
        "minecraft:redstone_block", DEACTIVATION_REDSTONE, 9, 160, 90
    ),
)  # type: RecipesCollection[GeneratorRecipe]
