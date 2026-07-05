# coding=utf-8
from ..define import id_enum
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.mixed_macerator import (
    MachineRecipe,
    MixedMaceratorRecipe,
    Input,
    Output,
)

STORE_RF_MAX = 14400

recipes = RecipesCollection(
    id_enum.Machinery.MIXED_MACERATOR,
    MixedMaceratorRecipe(
        {
            0: Input("minecraft:cobblestone"),
            1: Input("minecraft:sand"),
        },
        Output("minecraft:gravel"),
        40,
        240,
    ),
    MixedMaceratorRecipe(
        {
            0: Input("minecraft:gravel"),
            1: Input("minecraft:sand", 2),
            2: Input("minecraft:clay_ball"),
        },
        Output(id_enum.Dusts.CONCRETE, 8),
        40,
        160,
    ),
)  # type: RecipesCollection[MachineRecipe]
