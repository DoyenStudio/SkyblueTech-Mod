# coding=utf-8

from ..define.global_config import RAW2MOTTEN_VOLUME, INGOT2MOTTEN_VOLUME
from ..define.id_enum.fluids import *
from ..define.tag_enum.items import *
from ..mini_jei.machines.magma_furnace import *


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
        MOLTEN_IRON, RAW2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_gold", False,
        MOLTEN_GOLD, RAW2MOTTEN_VOLUME,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_copper", False,
        MOLTEN_COPPER, RAW2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        RawTag.TIN, True,
        MOLTEN_TIN, RAW2MOTTEN_VOLUME,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        RawTag.LEAD, True,
        MOLTEN_LEAD, RAW2MOTTEN_VOLUME,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        RawTag.NICKEL, True,
        MOLTEN_NICKEL, RAW2MOTTEN_VOLUME,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        RawTag.SILVER, True,
        MOLTEN_SILVER, RAW2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        RawTag.PLATINUM, True,
        MOLTEN_PLATINUM, RAW2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
    # mineral/ingot
        MagmaFurnaceRecipe(
        "minecraft:iron_ingot", False,
        MOLTEN_IRON, INGOT2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:gold_ingot", False,
        MOLTEN_GOLD, INGOT2MOTTEN_VOLUME,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:copper_ingot", False,
        MOLTEN_COPPER, INGOT2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.TIN, True,
        MOLTEN_TIN, INGOT2MOTTEN_VOLUME,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.LEAD, True,
        MOLTEN_LEAD, INGOT2MOTTEN_VOLUME,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        IngotTag.NICKEL, True,
        MOLTEN_NICKEL, INGOT2MOTTEN_VOLUME,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.SILVER, True,
        MOLTEN_SILVER, INGOT2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.PLATINUM, True,
        MOLTEN_PLATINUM, INGOT2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
] # type: list[MachineRecipe]