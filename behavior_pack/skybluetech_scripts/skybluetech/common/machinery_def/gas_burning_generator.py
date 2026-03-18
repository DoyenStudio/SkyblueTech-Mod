# coding=utf-8
from ..define.id_enum.fluids import METHANE
from ..mini_jei.machinery.gas_burning_generator import GasBurningGeneratorRecipe

recipes = {
    METHANE: GasBurningGeneratorRecipe(METHANE, 8, 160),
}
