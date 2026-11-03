# coding=utf-8
from ..define.id_enum import Machinery, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.thermal_cracker import ThermalCrackerRecipe

CHAMBER_HEAT_CAPACITY = 50.0
FLUID_SLOT_MAX_VOLUMES = {0: 2000, 1: 2000, 2: 2000, 3: 2000}
recipes = RecipesCollection(
    Machinery.THERMAL_CRACKER,
    ThermalCrackerRecipe(
        ((fluids.CommonOil.TREE_OIL, 100), (fluids.CommonGas.WATER_VAPOR, 200)),
        ((fluids.CommonGas.ETHYLENE, 400), (fluids.CommonGas.PURE_METHANE, 100)),
        1000, 1100, 1300, 2000, tick_duration=200,
    ),
)
