# coding=utf-8
from ..define.id_enum.fluids import METHANE
from ..mini_jei.machinery.gas_burning_generator import GasBurningRecipe

recipes = {
    METHANE: GasBurningRecipe(METHANE, 8, 160),
}
