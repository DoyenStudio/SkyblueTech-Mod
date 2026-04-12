# coding=utf-8
from ..define.id_enum import GAS_BURNING_GENERATOR, METHANE
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.gas_burning_generator import (
    GeneratorRecipe,
    GasBurningGeneratorRecipe,
)

recipes = RecipesCollection(
    GAS_BURNING_GENERATOR,
    GasBurningGeneratorRecipe(METHANE, 8, 160),
)  # type: RecipesCollection[GeneratorRecipe]
