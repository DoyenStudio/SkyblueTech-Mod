# coding=utf-8
from ..define.id_enum import COMPRESSOR, Plates
from ..define.tag_enum.items import IngotTag
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.compressor import (
    MachineRecipe,
    gen_preset_recipe,
    gen_preset_tagged_recipe,
)


DEFAULT_TICK_DURATION = 20 * 8
DEFAULT_POWER = 80


preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_preset_tagged_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)

recipes = RecipesCollection(
    COMPRESSOR,
    # Minecraft
    # Ingot 2 Plate
    preset("minecraft:copper_ingot", Plates.COPPER),
    preset("minecraft:iron_ingot", Plates.IRON),
    preset("minecraft:gold_ingot", Plates.GOLD),
    preset_tagged(IngotTag.TIN, Plates.TIN),
    preset_tagged(IngotTag.LEAD, Plates.LEAD),
    preset_tagged(IngotTag.SILVER, Plates.SILVER),
    preset_tagged(IngotTag.PLATINUM, Plates.PLATINUM),
    preset_tagged(IngotTag.NICKEL, Plates.NICKEL),
    preset_tagged(IngotTag.BRONZE, Plates.BRONZE),
    preset_tagged(IngotTag.STEEL, Plates.STEEL),
    preset_tagged(IngotTag.INVAR, Plates.INVAR),
    preset_tagged(IngotTag.ULTRAHEATINUM, Plates.ULTRAHEATINUM),
    preset_tagged(IngotTag.SUPERCONDUCT, Plates.SUPERCONDUCT),
)  # type: RecipesCollection[MachineRecipe]
