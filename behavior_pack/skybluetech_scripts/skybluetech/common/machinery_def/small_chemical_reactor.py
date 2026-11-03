# coding=utf-8
from ..define.id_enum import Machinery, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.define import CategoryType, Input, Output
from ..mini_jei.machinery.small_chemical_reactor import SmallChemicalReactorRecipe

STORE_RF_MAX = 32000
FLUID_SLOT_MAX_VOLUMES = {0: 2000, 1: 2000, 2: 2000}
recipes = RecipesCollection(
    Machinery.SMALL_CHEMICAL_REACTOR,
    SmallChemicalReactorRecipe(
        {CategoryType.FLUID: {0: Input(fluids.CommonGas.ETHYLENE, 400),
                              1: Input(fluids.CommonGas.OXYGEN, 40)}},
        {CategoryType.FLUID: {2: Output(fluids.HotFluid.MOLTEN_POLYETHYLENE, 144)}},
        power_cost=128, tick_duration=200,
    ),
)
