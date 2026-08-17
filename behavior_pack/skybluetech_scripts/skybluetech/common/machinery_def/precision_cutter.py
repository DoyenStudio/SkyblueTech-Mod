# coding=utf-8
from ..define import id_enum
from ..mini_jei.core import RecipesCollection
from ..mini_jei.machinery.precision_cutter import (
    MachineRecipe,
    PrecisionCutterRecipe,
    Input,
    Output,
)

STORE_RF_MAX = 8800
MAX_FLUID_VOLUME = 2000

CUTTER_LEVEL_MAPPING = {
    id_enum.Cutter.STEEL: 1,
}


recipes = RecipesCollection(
    id_enum.Machinery.PRECISION_CUTTER,
    # prismarine
    PrecisionCutterRecipe(
        Input("minecraft:prismarine"),
        {2: Output("minecraft:prismarine_shard", 4)},
        1,
        1,
        20,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:dark_prismarine"),
        {2: Output("minecraft:prismarine_shard", 8)},
        1,
        1,
        20,
        160,
    ),
    # amethyst
    PrecisionCutterRecipe(
        Input("minecraft:amethyst_block"),
        {2: Output("minecraft:amethyst_shard", 4)},
        1,
        1,
        25,
        160,
    ),
    # quartz
    PrecisionCutterRecipe(
        Input("minecraft:quartz_block"),
        {2: Output("minecraft:quartz", 4)},
        1,
        1,
        25,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:smooth_quartz"),
        {2: Output("minecraft:quartz", 4)},
        1,
        1,
        25,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:chiseled_quartz_block"),
        {2: Output("minecraft:quartz", 4)},
        1,
        1,
        25,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:quartz_pillar"),
        {2: Output("minecraft:quartz", 4)},
        1,
        1,
        25,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:quartz_bricks"),
        {2: Output("minecraft:quartz", 4)},
        1,
        1,
        25,
        160,
    ),
    # nether brick
    PrecisionCutterRecipe(
        Input("minecraft:nether_brick"),
        {2: Output("minecraft:netherbrick", 4)},
        1,
        1,
        15,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:chiseled_nether_bricks"),
        {2: Output("minecraft:netherbrick", 4)},
        1,
        1,
        15,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:cracked_nether_bricks"),
        {2: Output("minecraft:netherbrick", 4)},
        1,
        1,
        15,
        160,
    ),
    # red nether brick
    PrecisionCutterRecipe(
        Input("minecraft:red_nether_brick"),
        {2: Output("minecraft:netherbrick", 2)},
        1,
        1,
        15,
        160,
    ),
    # brick
    PrecisionCutterRecipe(
        Input("minecraft:brick_block"),
        {2: Output("minecraft:brick", 4)},
        1,
        1,
        15,
        160,
    ),
    # resin brick
    PrecisionCutterRecipe(
        Input("minecraft:resin_bricks"),
        {2: Output("minecraft:resin_brick", 4)},
        1,
        1,
        15,
        160,
    ),
    PrecisionCutterRecipe(
        Input("minecraft:chiseled_resin_bricks"),
        {2: Output("minecraft:resin_brick", 4)},
        1,
        1,
        15,
        160,
    ),
)  # type: RecipesCollection[MachineRecipe]
