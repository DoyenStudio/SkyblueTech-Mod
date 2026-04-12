# coding=utf-8
from ..mini_jei.core import RecipesCollection
from ..define.id_enum import MACERATOR, Dusts
from ..define.tag_enum.items import IngotTag, RawTag
from ..mini_jei.machinery.macerator import (
    MachineRecipe,
    gen_preset_recipe,
    gen_tagged_preset_recipe,
)


DEFAULT_TICK_DURATION = 160
DEFAULT_POWER = 30

preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_tagged_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)


recipes = RecipesCollection(
    MACERATOR,
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
    preset("minecraft:copper_ingot", 1, Dusts.COPPER, 1),
    preset("minecraft:iron_ingot", 1, Dusts.IRON, 1),
    preset("minecraft:gold_ingot", 1, Dusts.GOLD, 1),
    preset_tagged(IngotTag.TIN, 1, Dusts.TIN, 1),
    preset_tagged(IngotTag.LEAD, 1, Dusts.LEAD, 1),
    preset_tagged(IngotTag.SILVER, 1, Dusts.SILVER, 1),
    preset_tagged(IngotTag.PLATINUM, 1, Dusts.PLATINUM, 1),
    preset_tagged(IngotTag.NICKEL, 1, Dusts.NICKEL, 1),
    # Raw ore 2 Dust
    preset("minecraft:raw_copper", 1, Dusts.COPPER, 2),
    preset("minecraft:raw_iron", 1, Dusts.IRON, 2),
    preset("minecraft:raw_gold", 1, Dusts.GOLD, 2),
    preset_tagged(RawTag.TIN, 1, Dusts.TIN, 2),
    preset_tagged(RawTag.LEAD, 1, Dusts.LEAD, 2),
    preset_tagged(RawTag.SILVER, 1, Dusts.SILVER, 2),
    preset_tagged(RawTag.PLATINUM, 1, Dusts.PLATINUM, 2),
    preset_tagged(RawTag.NICKEL, 1, Dusts.NICKEL, 2),
)  # type: RecipesCollection[MachineRecipe]
