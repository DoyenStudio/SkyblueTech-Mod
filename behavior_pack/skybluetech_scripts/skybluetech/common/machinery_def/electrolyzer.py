# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.define import Output
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

CHLOR_ALKALI_INPUT_VOLUME = 100
CHLOR_ALKALI_HYDROGEN_VOLUME = 100
CHLOR_ALKALI_CHLORINE_VOLUME = 100
CHLOR_ALKALI_SODIUM_HYDROXIDE_VOLUME = 100
CHLOR_ALKALI_POWER_COST = 200
CHLOR_ALKALI_TICK_DURATION = 50

recipes = RecipesCollection(
    id_enum.Machinery.ELECTROLYZER,
    ElectrolyzerRecipe(
        input_fluid=id_enum.CommonLiquid.WATER,
        input_volume=4,
        output_fluid1=id_enum.CommonGas.HYDROGEN,
        output_volume1=20,
        output_fluid2=id_enum.CommonGas.OXYGEN,
        output_volume2=40,
        power_cost=200,
        tick_duration=10,
    ),
    ElectrolyzerRecipe(
        input_fluid=id_enum.CommonLiquid.DISTILLED_WATER,
        input_volume=4,
        output_fluid1=id_enum.CommonGas.HYDROGEN,
        output_volume1=20,
        output_fluid2=id_enum.CommonGas.OXYGEN,
        output_volume2=40,
        power_cost=200,
        tick_duration=10,
    ),
    ElectrolyzerRecipe(
        input_fluid=id_enum.CommonLiquid.SATURATED_BRINE,
        input_volume=CHLOR_ALKALI_INPUT_VOLUME,
        output_fluid1=id_enum.CommonGas.HYDROGEN,
        output_volume1=CHLOR_ALKALI_HYDROGEN_VOLUME,
        output_fluid2=id_enum.CommonGas.CHLORINE,
        output_volume2=CHLOR_ALKALI_CHLORINE_VOLUME,
        output_fluid3=id_enum.Alkali.SODIUM_HYDROXIDE_SOLUTION,
        output_volume3=CHLOR_ALKALI_SODIUM_HYDROXIDE_VOLUME,
        power_cost=CHLOR_ALKALI_POWER_COST,
        tick_duration=CHLOR_ALKALI_TICK_DURATION,
    ),
    ElectrolyzerRecipe(
        input_fluid=id_enum.Chemical.COPPER_SOLUTION,
        input_volume=250,
        output_fluid1=id_enum.Acid.SULFURIC_ACID,
        output_volume1=150,
        output_fluid2=id_enum.CommonLiquid.WATER,
        output_volume2=100,
        output_fluid3=id_enum.CommonGas.OXYGEN,
        output_volume3=50,
        output_item=Output(id_enum.Dusts.COPPER),
        power_cost=256,
        tick_duration=200,
    ),
    ElectrolyzerRecipe(
        input_fluid=id_enum.Chemical.NICKEL_SOLUTION,
        input_volume=250,
        output_fluid1=id_enum.Acid.SULFURIC_ACID,
        output_volume1=150,
        output_fluid2=id_enum.CommonLiquid.WATER,
        output_volume2=100,
        output_fluid3=id_enum.CommonGas.OXYGEN,
        output_volume3=50,
        output_item=Output(id_enum.Dusts.NICKEL),
        power_cost=384,
        tick_duration=200,
    ),
    ElectrolyzerRecipe(
        input_fluid=id_enum.Chemical.GOLD_SOLUTION,
        input_volume=250,
        output_fluid1=id_enum.Chemical.BARREN_HCL,
        output_volume1=100,
        output_fluid2=id_enum.CommonGas.CHLORINE,
        output_volume2=50,
        output_item=Output(id_enum.Dusts.GOLD),
        power_cost=384,
        tick_duration=200,
    ),
)  # type: RecipesCollection[ElectrolyzerRecipe]
