# coding=utf-8
#
from .define import PresetMachineRecipe

DEFAULT_TICK_DURATION = 160
DEFAULT_POWER = 90

preset = PresetMachineRecipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)


recipes = [
    # Minecraft 
    preset.SimpleXXRecipe("minecraft:bone", 1, "minecraft:bone_meal", 5),
    preset.SimpleXXRecipe("minecraft:clay", 1, "minecraft:clay_ball", 4),
    preset.Simple11Recipe("minecraft:stone", "minecraft:sand"),
    preset.Simple11Recipe("minecraft:cobblestone", "minecraft:sand"),
    preset.Simple11Recipe("minecraft:sand", "skybluetech:dust_block"),
    preset.Simple11Recipe("minecraft:lapis_lazuli", "skybluetech:lapis_dust"),
    preset.Simple11Recipe("minecraft:coal", "skybluetech:carbon_dust"),
    preset.Simple11Recipe("minecraft:charcoal", "skybluetech:carbon_dust"),
    preset.Simple11Recipe("minecraft:ancient_debris", "skybluetech:ancient_debris_dust"),
    # Ingot 2 Dust
    preset.Simple11Recipe("minecraft:copper_ingot", "skybluetech:copper_dust"), 
    preset.Simple11Recipe("minecraft:iron_ingot", "skybluetech:iron_dust"),
    preset.Simple11Recipe("minecraft:gold_ingot", "skybluetech:gold_dust"),
    preset.Simple11TagRecipe("ingots/tin", "skybluetech:tin_dust"),
    preset.Simple11TagRecipe("ingots/lead", "skybluetech:lead_dust"),
    preset.Simple11TagRecipe("ingots/silver", "skybluetech:silver_dust"),
    preset.Simple11TagRecipe("ingots/platinum", "skybluetech:platinum_dust"),
    preset.Simple11TagRecipe("ingots/nickel", "skybluetech:nickel_dust"),
    # Raw ore 2 Dust
    preset.SimpleXXRecipe("minecraft:raw_copper", 1, "skybluetech:copper_dust", 2), 
    preset.SimpleXXRecipe("minecraft:raw_iron", 1, "skybluetech:iron_dust", 2),
    preset.SimpleXXRecipe("minecraft:raw_gold", 1, "skybluetech:gold_dust", 2),
    preset.SimpleXXTagRecipe("raws/tin", 1, "skybluetech:tin_dust", 2),
    preset.SimpleXXTagRecipe("raws/lead", 1, "skybluetech:lead_dust", 2),
    preset.SimpleXXTagRecipe("raws/silver", 1, "skybluetech:silver_dust", 2),
    preset.SimpleXXTagRecipe("raws/platinum", 1, "skybluetech:platinum_dust", 2),
    preset.SimpleXXTagRecipe("raws/nickel", 1, "skybluetech:nickel_dust", 2),
]
