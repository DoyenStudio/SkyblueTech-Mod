# coding=utf-8
from ..define.id_enum import AIR_COMPRESSOR, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.air_compressor import AirCompressorRecipe

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 2000
COMPRESSED_AIR_OUTPUT_VOLUME = 50
K_PLACED_DIMENSION = "st:placed_dimension"
DIMENSION_OVERWORLD = 0
DIMENSION_NAMES = {
    0: "主世界",
    1: "下界",
    2: "末地",
}


recipes = RecipesCollection(
    AIR_COMPRESSOR,
    AirCompressorRecipe(
        DIMENSION_OVERWORLD,
        fluids.CommonGas.COMPRESSED_AIR,
        COMPRESSED_AIR_OUTPUT_VOLUME,
        tick_duration=10,
        power_cost=40,
    ),
)


def GetDimensionName(dimension):
    # type: (int) -> str
    return DIMENSION_NAMES.get(dimension, "未知")


def GetRecipeByDimension(dimension):
    # type: (int | None) -> AirCompressorRecipe | None
    for recipe in recipes:
        if recipe.dimension == dimension:
            return recipe
    return None
