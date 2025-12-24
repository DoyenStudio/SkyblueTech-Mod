# coding=utf-8
#
from ..define.tag_enum.items import *
from ..define.id_enum.items import *
from ..mini_jei.machines.compressor import *


DEFAULT_TICK_DURATION = 20 * 8
DEFAULT_POWER = 80


preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_preset_tagged_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)

recipes = [
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
] # type: list[MachineRecipe]