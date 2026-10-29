# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.electrolyzer import (
    ElectrolyzerRecipe,
)

STORE_RF_MAX = 8000
MAX_FLUID_VOLUME = 2000
OUTPUT_FLUID_VOLUME = 500
FLUID_SLOT_MAX_VOLUMES = {
    0: MAX_FLUID_VOLUME,
    1: OUTPUT_FLUID_VOLUME,
    2: OUTPUT_FLUID_VOLUME,
    3: OUTPUT_FLUID_VOLUME,
}

recipes = RecipesCollection(
    id_enum.Machinery.ELECTROLYZER,
    ElectrolyzerRecipe(
        input_fluid=id_enum.CommonLiquid.WATER,
        input_volume=4,
        output_fluid1=id_enum.CommonGas.OXYGEN,
        output_volume1=20,
        output_fluid2=id_enum.CommonGas.HYDROGEN,
        output_volume2=40,
        power_cost=480,
        tick_duration=10,
    ),
)  # type: RecipesCollection[ElectrolyzerRecipe]
