# coding=utf-8
#

from ...mini_jei.machines.alloy_furnace import *


DEFAULT_TICK_DURATION = 160
DEFAULT_POWER = 80
L_TICK_DURATION = 200
L_POWER = 120

preset1 = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset2 = gen_preset_recipe(L_POWER, L_TICK_DURATION)

# preset = PresetMachineRecipe(MACHINE_ID, DEFAULT_POWER, DEFAULT_TICK_DURATION)
# preset2 = PresetMachineRecipe(MACHINE_ID, L_POWER, L_TICK_DURATION)

TAG_TIN_DUST = "dusts/tin"
TAG_COPPER_DUST = "dusts/copper"
TAG_IRON_DUST = "dusts/iron"
TAG_NICKEL_DUST = "dusts/nickel"
TAG_CARBON_DUST = "dusts/carbon"
TAG_ANCIENT_DEBRIS_DUST = "dusts/ancient_debris"

TAG_TIN_INGOT = "ingots/tin"
TAG_NICKEL_INGOT = "ingots/nickel"

recipes = [
    # Alloy
    preset1(
        {0: Input(TAG_COPPER_DUST, 3, True), 1: Input(TAG_TIN_DUST, 1, True)},
        {4: Output("skybluetech:bronze_ingot", 4)}
    ),
    preset2(
        {0: Input("minecraft:copper_ingot", 3), 1: Input(TAG_TIN_INGOT, 1, True)},
        {4: Output("skybluetech:bronze_ingot", 4)}
    ),
    preset1(
        {0: Input(TAG_IRON_DUST, 2, True), 1: Input(TAG_NICKEL_DUST, 1, True)},
        {4: Output("skybluetech:invar_ingot", 3)}
    ),
    preset2(
        {0: Input("minecraft:iron_ingot", 3), 1: Input(TAG_NICKEL_INGOT, 1, True)},
        {4: Output("skybluetech:invar_ingot", 4)}
    ),
    preset1(
        {0: Input(TAG_IRON_DUST, 1, True), 2: Input(TAG_CARBON_DUST, 1, True)},
        {4: Output("skybluetech:steel_ingot", 1)}
    ),
    preset2(
        {0: Input("minecraft:iron_ingot", 1), 2: Input(TAG_CARBON_DUST, 1, True)},
        {4: Output("skybluetech:steel_ingot", 1)}
    ),
    preset2(
        {0: Input("minecraft:gold_ingot", 2), 2: Input(TAG_ANCIENT_DEBRIS_DUST, 3, True)},
        {4: Output("minecraft:netherite_ingot", 1)}
    )
]
