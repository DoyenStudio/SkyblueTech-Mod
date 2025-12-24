# coding=utf-8
#
from ..mini_jei.machines.macerator import *


DEFAULT_TICK_DURATION = 160
DEFAULT_POWER = 90

preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_tagged_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)


recipes = [
    # Minecraft 
    preset("minecraft:bone", 1, "minecraft:bone_meal", 5),
    preset("minecraft:clay", 1, "minecraft:clay_ball", 4),
    preset("minecraft:stone", 1, "minecraft:sand", 1),
    preset("minecraft:cobblestone", 1, "minecraft:sand", 1),
    preset("minecraft:sand", 1, "skybluetech:dust_block", 1),
    preset("minecraft:lapis_lazuli", 1, "skybluetech:lapis_dust", 1),
    preset("minecraft:coal", 1, "skybluetech:carbon_dust", 1),
    preset("minecraft:charcoal", 1, "skybluetech:carbon_dust", 1),
    preset("minecraft:ancient_debris", 1, "skybluetech:ancient_debris_dust", 1),
    # Ingot 2 Dust
    preset("minecraft:copper_ingot", 1, "skybluetech:copper_dust", 1), 
    preset("minecraft:iron_ingot", 1, "skybluetech:iron_dust", 1),
    preset("minecraft:gold_ingot", 1, "skybluetech:gold_dust", 1),
    preset_tagged("ingots/tin", 1, "skybluetech:tin_dust", 1),
    preset_tagged("ingots/lead", 1, "skybluetech:lead_dust", 1),
    preset_tagged("ingots/silver", 1, "skybluetech:silver_dust", 1),
    preset_tagged("ingots/platinum", 1, "skybluetech:platinum_dust", 1),
    preset_tagged("ingots/nickel", 1, "skybluetech:nickel_dust", 1),
    # Raw ore 2 Dust
    preset("minecraft:raw_copper", 1, "skybluetech:copper_dust", 2), 
    preset("minecraft:raw_iron", 1, "skybluetech:iron_dust", 2),
    preset("minecraft:raw_gold", 1, "skybluetech:gold_dust", 2),
    preset_tagged("raws/tin", 1, "skybluetech:tin_dust", 2),
    preset_tagged("raws/lead", 1, "skybluetech:lead_dust", 2),
    preset_tagged("raws/silver", 1, "skybluetech:silver_dust", 2),
    preset_tagged("raws/platinum", 1, "skybluetech:platinum_dust", 2),
    preset_tagged("raws/nickel", 1, "skybluetech:nickel_dust", 2),
]
