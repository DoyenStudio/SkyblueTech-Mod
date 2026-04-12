# coding=utf-8
#
from ..define.id_enum import ALLOY_FURNACE, Ingots
from ..define.tag_enum.items import DustTag, IngotTag
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.alloy_furnace import (
    MachineRecipe,
    Input,
    Output,
    gen_preset_recipe,
)


DEFAULT_TICK_DURATION = 160
DEFAULT_POWER = 80
L_TICK_DURATION = 240
L_POWER = 120

preset1 = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset2 = gen_preset_recipe(L_POWER, L_TICK_DURATION)


recipes = RecipesCollection(
    ALLOY_FURNACE,
    # Alloy
    preset1(
        {0: Input(DustTag.COPPER, 3, True), 1: Input(DustTag.TIN, 1, True)},
        {4: Output(Ingots.BRONZE, 4)},
    ),
    preset2(
        {0: Input("minecraft:copper_ingot", 3), 1: Input(IngotTag.TIN, 1, True)},
        {4: Output(Ingots.BRONZE, 4)},
    ),
    preset1(
        {0: Input(DustTag.IRON, 2, True), 1: Input(DustTag.NICKEL, 1, True)},
        {4: Output(Ingots.INVAR, 3)},
    ),
    preset2(
        {0: Input("minecraft:iron_ingot", 2), 1: Input(IngotTag.NICKEL, 1, True)},
        {4: Output(Ingots.INVAR, 3)},
    ),
    preset1(
        {0: Input(DustTag.IRON, 1, True), 2: Input(DustTag.CARBON, 1, True)},
        {4: Output(Ingots.STEEL, 1)},
    ),
    preset2(
        {0: Input("minecraft:iron_ingot", 1), 2: Input(DustTag.CARBON, 1, True)},
        {4: Output(Ingots.STEEL, 1)},
    ),
    preset2(
        {
            0: Input("minecraft:gold_ingot", 2),
            2: Input(DustTag.ANCIENT_DEBRIS, 3, True),
        },
        {4: Output("minecraft:netherite_ingot", 1)},
    ),
    preset2(
        {
            0: Input(DustTag.SILVER, is_tag=True),
            1: Input(DustTag.PLATINUM, is_tag=True),
            2: Input(DustTag.LAPIS, is_tag=True),
        },
        {4: Output(Ingots.SUPERCONDUCT, 2)},
    ),
)  # type: RecipesCollection[MachineRecipe]
