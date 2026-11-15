# coding=utf-8
from ..define.id_enum import Machinery, Ingots, Sticks
from ..define.id_enum import fluids
from ..misc.inscriber_press import STICK as INSCRIBER_PRESS_STICK
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.metal_press import Input, MachineRecipe, MetalPressRecipe

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 1000

recipes = RecipesCollection(
    Machinery.METAL_PRESS,
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input("minecraft:copper_ingot", 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.COPPER,
        2,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input("minecraft:iron_ingot", 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.IRON,
        2,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.ALUMINUM, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.ALUMINUM,
        2,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.TIN, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.TIN,
        2,
        tick_duration=60,
        power_cost=40,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.SILVER, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.SILVER,
        2,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.PLATINUM, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.PLATINUM,
        2,
        tick_duration=40,
        power_cost=40,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.STEEL, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.STEEL,
        2,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.BRONZE, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.BRONZE,
        2,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.INVAR, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.INVAR,
        2,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.CUPRONICKEL, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.CUPRONICKEL,
        2,
        tick_duration=60,
        power_cost=50,
    ),
    MetalPressRecipe(
        fluids.CommonOil.LUBRICANT,
        10,
        [Input(Ingots.SUPERCONDUCT, 1), Input(INSCRIBER_PRESS_STICK, 0)],
        Sticks.SUPERCONDUCT,
        2,
        tick_duration=60,
        power_cost=50,
    ),
)  # type: RecipesCollection[MachineRecipe]
