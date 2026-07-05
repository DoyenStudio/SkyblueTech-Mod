# coding=utf-8
from ..define import id_enum, tag_enum
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.mixer import MachineRecipe, MixerRecipe

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 2000

recipes = RecipesCollection(
    id_enum.Machinery.MIXER,
    MixerRecipe(
        "minecraft:lava",
        500,
        "minecraft:netherrack",
        1,
        "minecraft:magma",
        1,
        tick_duration=80,
        power_cost=40,
    ),
    MixerRecipe(
        "minecraft:water",
        400,
        id_enum.DUST_BLOCK,
        1,
        "minecraft:clay",
        1,
        tick_duration=40,
        power_cost=30,
    ),
    MixerRecipe(
        None,
        0,
        id_enum.Dusts.LEAD,
        1,
        id_enum.Dusts.LEAD_OXIDE,
        1,
        tick_duration=60,
        power_cost=35,
    ),
    MixerRecipe(
        id_enum.fluids.Acid.SULFURIC_ACID,
        250,
        id_enum.Dusts.LEAD_OXIDE,
        1,
        id_enum.Dusts.LEAD_SULFATE,
        1,
        tick_duration=50,
        power_cost=30,
    ),
    MixerRecipe(
        "minecraft:water",
        1000,
        id_enum.Dusts.CONCRETE,
        4,
        "minecraft:concrete",
        1,
        tick_duration=50,
        power_cost=30,
    ),
)  # type: RecipesCollection[MachineRecipe]
