# coding=utf-8
from ..define.id_enum import Machinery, fluids, items
from ..define.resin import RESIN_FLUID_VOLUME
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.heat_melting_chamber import HeatMeltingChamberRecipe

MIN_KELVIN = 300.0
MAX_KELVIN = 900.0
CHAMBER_HEAT_CAPACITY = 50.0
OUTPUT_MAX_VOLUME = 1500
K_PROGRESS = "st:melting_progress"
K_RECIPE_INPUT = "st:melting_input"
K_SPEED = "st:melting_speed"
K_DURATION = "st:melting_duration"
K_OVERHEATED = "st:melting_overheated"

# 沿用原熔化仓草稿的松香配方；耗热单位为 RF热/mB，可逐配方设置。
recipes = RecipesCollection(
    Machinery.HEAT_MELTING_CHAMBER,
    HeatMeltingChamberRecipe(
        items.RESIN, fluids.CommonLiquid.LIQUID_RESIN, RESIN_FLUID_VOLUME,
        tick_duration=200, min_temperature=333, fit_temperature=343,
        max_temperature=373, heat_per_produce=1.0,
    ),
    HeatMeltingChamberRecipe(
        items.ROSIN, fluids.Molten.ROSIN, 144,
        tick_duration=200, min_temperature=333,
        fit_temperature=343, max_temperature=353,
        heat_per_produce=1.0,
    ),
)
