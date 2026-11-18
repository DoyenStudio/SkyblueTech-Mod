# coding=utf-8
from ..define.id_enum import (
    Acid, Alkali, Chemical, ChemicalGas, CommonLiquid, Dusts, FilterCakes, Machinery,
)
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.define import CategoryType, Input, Output
from ..mini_jei.machinery.industrial_centrifuge import IndustrialCentrifugeRecipe

STORE_RF_MAX = 32000
FLUID_SLOT_MAX_VOLUMES = {0: 8000, 1: 2000, 2: 2000}
K_WORKING = "centrifugeWorking"
K_BATCH_FLUID = "centrifugeBatchFluid"
recipes = RecipesCollection(Machinery.INDUSTRIAL_CENTRIFUGE)


def _add(feed, first, second=None, solid=None, power=128, ticks=200, heat=(0, 0, 0)):
    liquids = {1: Output(*first)}
    if second:
        liquids[2] = Output(*second)
    outputs = {CategoryType.FLUID: liquids}
    if solid:
        outputs[CategoryType.ITEM] = {0: Output(solid, 1)}
    recipe = IndustrialCentrifugeRecipe(
        inputs={CategoryType.FLUID: {0: Input(*feed)}}, outputs=outputs,
        power_cost=power, tick_duration=ticks, heat=heat,
    )
    recipes.add_recipe(recipe)
    return recipe


# P1, P3 (also PM-R2)
_add((Chemical.FLOTATION_WASTE, 300), (Chemical.MINERAL_COLLECTOR, 100),
     (CommonLiquid.ORGANIC_WASTE, 200))
_add((CommonLiquid.PROCESS_WATER, 50), (CommonLiquid.WATER, 50))

# N2, N3
_add((Chemical.CALCIUM_LIQUOR, 400), (CommonLiquid.CALCIUM_CHLORIDE, 400), ticks=100)
CALCIUM_CRYSTALLIZATION = _add(
    (CommonLiquid.CALCIUM_CHLORIDE, 400), (CommonLiquid.WATER, 400),
    solid=Dusts.CALCIUM_CHLORIDE, ticks=100, heat=(370, 390, 200),
)

# SNW1, SNW3, CU4, NI4
_add((Chemical.TIN_ACID_WASTE, 250), (Chemical.HYDROCHLORIC_ACID, 150),
     (Chemical.TIN_DEACID_WASTE, 100))
_add((Chemical.TIN_NEUTRAL_LIQ, 125), (CommonLiquid.WATER, 100),
     (CommonLiquid.DILUTE_BRINE, 25))
_add((Chemical.COPPER_LEACH, 250), (Chemical.COPPER_SOLUTION, 250))
_add((Chemical.NICKEL_LEACH, 250), (Chemical.NICKEL_SOLUTION, 250))

# PM-R1, AG-5
_add((Chemical.BARREN_HCL, 100), (Chemical.HYDROCHLORIC_ACID, 50),
     (CommonLiquid.PROCESS_WATER, 50))
_add((Chemical.SILVER_SLURRY, 250), (Chemical.BARREN_HCL, 150),
     solid=FilterCakes.SILVER_CHLORIDE)

# AL6, TI0, TI6, MG4
_add((Chemical.ALKALI_LIQUOR, 250), (Alkali.SODIUM_HYDROXIDE_SOLUTION, 200),
     (CommonLiquid.WATER, 50), power=120, ticks=100, heat=(370, 390, 300))
_add((Acid.SULFURIC_ACID, 250), (Acid.CONCENTRATED_SULFURIC_ACID, 200),
     (CommonLiquid.WATER, 50), heat=(430, 470, 400))
_add((Chemical.TITANIUM_ACID, 250), (Acid.CONCENTRATED_SULFURIC_ACID, 200),
     (CommonLiquid.WATER, 50), power=160, ticks=100, heat=(430, 470, 400))
_add((ChemicalGas.ACID_VAPOR, 150), (Acid.HYDROGEN_CHLORIDE, 50),
     (CommonLiquid.WATER, 100), power=120, ticks=100)
