# coding=utf-8
from ..define import id_enum
from ..define.id_enum import Machinery, Plates
from ..define.tag_enum.items import IngotTag, PlateTag
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.compressor import (
    MachineRecipe,
    CompressorRecipe,
    Input,
    Output,
    gen_preset_recipe,
    gen_preset_tagged_recipe,
)

STORE_RF_MAX = 8800

DEFAULT_TICK_DURATION = 20 * 8
DEFAULT_POWER = 80


preset = gen_preset_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)
preset_tagged = gen_preset_tagged_recipe(DEFAULT_POWER, DEFAULT_TICK_DURATION)

recipes = RecipesCollection(
    Machinery.COMPRESSOR,
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
    preset_tagged(IngotTag.ALUMITE, Plates.ALUMITE),
    preset_tagged(IngotTag.STEEL, Plates.STEEL),
    preset_tagged(IngotTag.INVAR, Plates.INVAR),
    preset_tagged(IngotTag.CUPRONICKEL, Plates.CUPRONICKEL),
    preset_tagged(IngotTag.ULTRAHEATINUM, Plates.ULTRAHEATINUM),
    preset_tagged(IngotTag.SUPERCONDUCT, Plates.SUPERCONDUCT),
    # other
    CompressorRecipe(
        {
            0: Input("minecraft:lapis_lazuli"),
            1: Input(PlateTag.TIN, is_tag=True),
            2: Input(PlateTag.SILVER, is_tag=True),
        },
        Output(id_enum.Upgraders.EMPTY),
        DEFAULT_POWER,
        DEFAULT_TICK_DURATION,
    ),
    CompressorRecipe(
        {
            0: Input("minecraft:redstone"),
            1: Input(PlateTag.BRONZE, is_tag=True),
            2: Input(PlateTag.GOLD, is_tag=True),
        },
        Output(id_enum.ObjectUpgraders.PLATE_COMMON),
        DEFAULT_POWER,
        DEFAULT_TICK_DURATION,
    ),
    CompressorRecipe(
        {
            0: Input("minecraft:emerald"),
            1: Input(PlateTag.BRONZE, is_tag=True),
            2: Input(id_enum.CIRCUIT_BASE_PLATE),
        },
        Output(id_enum.ObjectUpgraders.PLATE_SPEC),
        DEFAULT_POWER,
        DEFAULT_TICK_DURATION,
    ),
    CompressorRecipe(
        {
            0: Input(id_enum.ControlCircuit.ADVANCED),
            1: Input("minecraft:diamond"),
            2: Input(PlateTag.TIN, is_tag=True),
        },
        Output(id_enum.INSCRIBING_TEMPLATE),
        DEFAULT_POWER,
        DEFAULT_TICK_DURATION,
    ),
)  # type: RecipesCollection[MachineRecipe]
