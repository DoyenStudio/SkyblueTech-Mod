# coding=utf-8
from ..define.id_enum import Machinery, MINERAL_ASH, SEMI_COKE, fluids
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.thermal_cracker import ThermalCrackerRecipe

CHAMBER_HEAT_CAPACITY = 50.0
FLUID_SLOT_MAX_VOLUMES = {0: 8000, 1: 8000, 2: 8000, 3: 8000}
K_BATCH = "thermal_cracker_batch"
K_BATCH_WORK = "thermal_cracker_batch_work"
K_BATCH_PROGRESS = "thermal_cracker_batch_progress"

recipes = RecipesCollection(
    Machinery.THERMAL_CRACKER,
    ThermalCrackerRecipe(
        ((fluids.CommonOil.TREE_OIL, 100), (fluids.CommonGas.WATER_VAPOR, 200)),
        ((fluids.CommonGas.ETHYLENE, 400), (fluids.CommonGas.PURE_METHANE, 100)),
        1000, 1100, 1300, 2000, tick_duration=200,
    ),
    ThermalCrackerRecipe(
        ((fluids.CommonLiquid.WATER, 1000),),
        ((fluids.Chemical.COAL_TAR, 4000), (fluids.CommonLiquid.ORGANIC_WASTE, 1000)),
        750, 900, None, 6000, tick_duration=400, recipe_id="c1",
        solid_in=("minecraft:coal", 4), solid_out=(SEMI_COKE, 4),
    ),
    ThermalCrackerRecipe(
        ((fluids.CommonLiquid.WATER, 400),),
        ((fluids.Chemical.WOOD_CREOSOTE, 1000), (fluids.CommonLiquid.ORGANIC_WASTE, 400)),
        650, 800, None, 3000, tick_duration=300, recipe_id="w1",
        solid_in=("log", 4), solid_out=("minecraft:charcoal", 4), solid_in_is_tag=True,
    ),
)
recipes.add_recipe(ThermalCrackerRecipe(
    ((fluids.CommonGas.OXYGEN, 1000), (fluids.CommonGas.WATER_VAPOR, 2000)),
    ((fluids.Chemical.MINERAL_COLLECTOR, 3200), (fluids.CommonLiquid.ORGANIC_WASTE, 200)),
    1200, 1400, None, 60000, tick_duration=1200, recipe_id="f1",
    solid_in=("minecraft:coal", 1), solid_out=(MINERAL_ASH, 1),
))
