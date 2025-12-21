# coding=utf-8
#
from .define import PresetMachineRecipe

DEFAULT_TICK_DURATION = 20 * 8
DEFAULT_POWER = 80

preset = PresetMachineRecipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)


recipes = [
    # Minecraft
    # Ingot 2 Plate
    preset.Simple11Recipe("minecraft:copper_ingot", "skybluetech:copper_plate"), 
    preset.Simple11Recipe("minecraft:iron_ingot", "skybluetech:iron_plate"),
    preset.Simple11Recipe("minecraft:gold_ingot", "skybluetech:gold_plate"),
    preset.Simple11TagRecipe("ingots/tin", "skybluetech:tin_plate"),
    preset.Simple11TagRecipe("ingots/lead", "skybluetech:lead_plate"),
    preset.Simple11TagRecipe("ingots/silver", "skybluetech:silver_plate"),
    preset.Simple11TagRecipe("ingots/platinum", "skybluetech:platinum_plate"),
    preset.Simple11TagRecipe("ingots/nickel", "skybluetech:nickel_plate"),
]
