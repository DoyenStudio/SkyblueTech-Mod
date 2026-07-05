# coding=utf-8
from ..define.id_enum import Machinery, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.gas_burning_generator import (
    GeneratorRecipe,
    GasBurningGeneratorRecipe,
)

MAX_INPUT_GAS_VOLUME = 2000
MAX_OUTPUT_GAS_VOLUME = 2000
STORE_RF_MAX = 28800


recipes = RecipesCollection(
    Machinery.GAS_BURNING_GENERATOR,
    GasBurningGeneratorRecipe(fluids.CommonGas.METHANE, 4, 160),
)  # type: RecipesCollection[GeneratorRecipe]
