# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    BrineEvaporationPond,
    CommonLiquid,
)
from skybluetech_scripts.skybluetech.common.machinery_def.fluid_interface import (
    FLUID_INTERFACE_MAX_VOLUME,
)
from skybluetech_scripts.skybluetech.common.mini_jei.core import RecipesCollection
from skybluetech_scripts.skybluetech.common.mini_jei.machinery.brine_evaporation_pond import (
    BrineEvaporationPondRecipe,
)
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    GenerateSimpleStructureTemplate,
)

CONTROLLER = BrineEvaporationPond.CONTROLLER
IO_FLUID1 = BrineEvaporationPond.IO_FLUID1
IO_FLUID2 = BrineEvaporationPond.IO_FLUID2
IO_HEAT = BrineEvaporationPond.IO_HEAT

INPUT_MAX_VOLUME = FLUID_INTERFACE_MAX_VOLUME
OUTPUT_MAX_VOLUME = FLUID_INTERFACE_MAX_VOLUME
CHAMBER_HEAT_CAPACITY = 50.0
MIN_DISPLAY_TEMPERATURE = 300.0
MAX_DISPLAY_TEMPERATURE = 370.0
K_FLUID_RENDER_ORIGIN = "st:pond_fluid_origin"
K_FLUID_RENDER_SIZE = "st:pond_fluid_size"

recipes = RecipesCollection(
    CONTROLLER,
    BrineEvaporationPondRecipe(
        CommonLiquid.DILUTE_BRINE,
        25.0,
        CommonLiquid.SATURATED_BRINE,
        10.0,
        min_temperature=350.0,
        fit_temperature=360.0,
        heat_cost=20.0,
    ),
)

STRUCTURE_PALETTE_DICT = {
    0: ["Bb#bB", "bCCCb", "bCCCb", "bCCCb", "BbbbB"],
    1: ["BhhhB", "h...h", "h...h", "h...h", "BhhhB"],
    4: ["BBBBB", "BWWWB", "BWWWB", "BWWWB", "BBBBB"],
}
for i in range(2, 4):
    STRUCTURE_PALETTE_DICT[i] = ["BgggB", "g...g", "g...g", "g...g", "BgggB"]

STRUCTURE_REQUIRE_BLOCKS = {IO_HEAT: 1, IO_FLUID1: 1, IO_FLUID2: 1}

STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    {
        "B": "minecraft:brick_block",
        "b": [IO_HEAT, "minecraft:brick_block"],
        "C": "minecraft:waxed_copper",
        "g": ["minecraft:brick_block", "minecraft:glass"],
        "h": ["minecraft:brick_block", "minecraft:glass", IO_FLUID1, IO_FLUID2],
        "W": "minecraft:waxed_copper_grate",
    },
    STRUCTURE_PALETTE_DICT,
    "#",
    require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
)
