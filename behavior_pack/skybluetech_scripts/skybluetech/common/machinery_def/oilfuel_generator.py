# coding=utf-8
from ..define.id_enum import Machinery
from ..define.id_enum.fluids import CommonOil
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.oilfuel_generator import OilFuelGeneratorRecipe

MAX_INPUT_FUEL_VOLUME = 2000
STORE_RF_MAX = 16000
K_MODEL_YAW = "st:model_yaw"

recipes = RecipesCollection(
    Machinery.OILFUEL_GENERATOR,
    OilFuelGeneratorRecipe(CommonOil.FUEL_OIL, 50, output_power=320, tick_duration=20),
)  # type: RecipesCollection[OilFuelGeneratorRecipe]
