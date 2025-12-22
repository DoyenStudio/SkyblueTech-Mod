# coding=utf-8
#
from ...mini_jei.machines.magma_furnace import *


recipes = [
    # lava
    MagmaFurnaceRecipe(
        "minecraft:magma", False,
        "minecraft:lava", 1000,
        power_cost=40, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:cobblestone", False,
        "minecraft:lava", 250,
        power_cost=160, tick_duration=sec(20)
    ),
    MagmaFurnaceRecipe(
        "minecraft:obsidian", False,
        "minecraft:lava", 1000,
        power_cost=160, tick_duration=sec(14)
    ),
    MagmaFurnaceRecipe(
        "minecraft:netherrack", False,
        "minecraft:lava", 250,
        power_cost=75, tick_duration=sec(8)
    ),
    # mineral/raw
    MagmaFurnaceRecipe(
        "minecraft:raw_iron", False,
        "skybluetech:molten_iron", raw2motten_vol,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_gold", False,
        "skybluetech:molten_gold", raw2motten_vol,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_copper", False,
        "skybluetech:molten_copper", raw2motten_vol,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        "raws/tin", True,
        "skybluetech:molten_tin", raw2motten_vol,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        "raws/lead", True,
        "skybluetech:molten_lead", raw2motten_vol,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        "raws/nickel", True,
        "skybluetech:molten_nickel", raw2motten_vol,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        "raws/silver", True,
        "skybluetech:molten_silver", raw2motten_vol,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "raws/platinum", True,
        "skybluetech:molten_platinum", raw2motten_vol,
        power_cost=45, tick_duration=sec(4.5)
    ),
    # mineral/ingot
        MagmaFurnaceRecipe(
        "minecraft:iron_ingot", False,
        "skybluetech:molten_iron", ingot2motten_vol,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:gold_ingot", False,
        "skybluetech:molten_gold", ingot2motten_vol,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:copper_ingot", False,
        "skybluetech:molten_copper", ingot2motten_vol,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        "ingots/tin", True,
        "skybluetech:molten_tin", ingot2motten_vol,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        "ingots/lead", True,
        "skybluetech:molten_lead", ingot2motten_vol,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        "ingots/nickel", True,
        "skybluetech:molten_nickel", ingot2motten_vol,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        "ingots/silver", True,
        "skybluetech:molten_silver", ingot2motten_vol,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "ingots/platinum", True,
        "skybluetech:molten_platinum", ingot2motten_vol,
        power_cost=45, tick_duration=sec(4.5)
    ),
]