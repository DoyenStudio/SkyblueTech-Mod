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
        Molten.IRON, RAW2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_gold", False,
        Molten.GOLD, RAW2MOTTEN_VOLUME,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:raw_copper", False,
        Molten.COPPER, RAW2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        RawTag.TIN, True,
        Molten.TIN, RAW2MOTTEN_VOLUME,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        RawTag.LEAD, True,
        Molten.LEAD, RAW2MOTTEN_VOLUME,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        RawTag.NICKEL, True,
        Molten.NICKEL, RAW2MOTTEN_VOLUME,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        RawTag.SILVER, True,
        Molten.SILVER, RAW2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        RawTag.PLATINUM, True,
        Molten.PLATINUM, RAW2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
    # mineral/ingot
        MagmaFurnaceRecipe(
        "minecraft:iron_ingot", False,
        Molten.IRON, INGOT2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(8)
    ),
    MagmaFurnaceRecipe(
        "minecraft:gold_ingot", False,
        Molten.GOLD, INGOT2MOTTEN_VOLUME,
        power_cost=40, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        "minecraft:copper_ingot", False,
        Molten.COPPER, INGOT2MOTTEN_VOLUME,
        power_cost=50, tick_duration=sec(5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.TIN, True,
        Molten.TIN, INGOT2MOTTEN_VOLUME,
        power_cost=60, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.LEAD, True,
        Molten.LEAD, INGOT2MOTTEN_VOLUME,
        power_cost=70, tick_duration=sec(6)
    ),
    MagmaFurnaceRecipe(
        IngotTag.NICKEL, True,
        Molten.NICKEL, INGOT2MOTTEN_VOLUME,
        power_cost=65, tick_duration=sec(5.5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.SILVER, True,
        Molten.SILVER, INGOT2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
    MagmaFurnaceRecipe(
        IngotTag.PLATINUM, True,
        Molten.PLATINUM, INGOT2MOTTEN_VOLUME,
        power_cost=45, tick_duration=sec(4.5)
    ),
] # type: list[MachineRecipe]