# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    Chemical, ChemicalGas, CommonGas, Ingots, Machinery, MAGNESIUM_PELLET, Mixtures,
)
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import CategoryType, Input, Output
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.high_temp_electrolyzer import HighTempElectrolyzerRecipe

STORE_RF_MAX = 32000
FLUID_SLOT_MAX_VOLUMES = {0: 2000, 1: 500}
K_BATCH = "highTempElectrolysisBatch"

recipes = RecipesCollection(
    Machinery.HIGH_TEMP_ELECTROLYZER,
    HighTempElectrolyzerRecipe(
        "AL9", "铝电解",
        inputs={CategoryType.ITEM: {0: Input(Mixtures.ALUMINUM_ELECTROLYSIS, 1)}},
        outputs={
            CategoryType.ITEM: {1: Output(Ingots.ALUMINUM, 1)},
            CategoryType.FLUID: {1: Output(ChemicalGas.CARBON_DIOXIDE, 100)},
        },
        power_cost=400, tick_duration=200, heat=(1230, 1270, 1000),
    ),
    HighTempElectrolyzerRecipe(
        "MG5", "无水氯化镁熔盐电解",
        inputs={CategoryType.FLUID: {0: Input(Chemical.MOLTEN_MGCL2, 250)}},
        outputs={
            CategoryType.ITEM: {1: Output(MAGNESIUM_PELLET, 1)},
            CategoryType.FLUID: {1: Output(CommonGas.CHLORINE, 100)},
        },
        power_cost=400, tick_duration=200, heat=(1000, 1030, 1000),
    ),
)
