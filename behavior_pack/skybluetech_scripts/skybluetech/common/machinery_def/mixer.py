# coding=utf-8
from ..define.id_enum import MIXER, DUST_BLOCK
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.mixer import MachineRecipe, MixerRecipe


recipes = RecipesCollection(
    MIXER,
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
        DUST_BLOCK,
        1,
        "minecraft:clay",
        1,
        tick_duration=40,
        power_cost=30,
    ),
)  # type: RecipesCollection[MachineRecipe]
