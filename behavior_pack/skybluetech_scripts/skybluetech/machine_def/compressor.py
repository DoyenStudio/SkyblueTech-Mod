# coding=utf-8
#
from ..mini_jei.machines.compressor import *


DEFAULT_TICK_DURATION = 20 * 8
DEFAULT_POWER = 80


preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_preset_tagged_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)

recipes = [
    # Minecraft
    # Ingot 2 Plate
    preset("minecraft:copper_ingot", "skybluetech:copper_plate"), 
    preset("minecraft:iron_ingot", "skybluetech:iron_plate"),
    preset("minecraft:gold_ingot", "skybluetech:gold_plate"),
    preset_tagged("ingots/tin", "skybluetech:tin_plate"),
    preset_tagged("ingots/lead", "skybluetech:lead_plate"),
    preset_tagged("ingots/silver", "skybluetech:silver_plate"),
    preset_tagged("ingots/platinum", "skybluetech:platinum_plate"),
    preset_tagged("ingots/nickel", "skybluetech:nickel_plate"),
] # type: list[MachineRecipe]
