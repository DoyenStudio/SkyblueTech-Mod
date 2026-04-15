# coding=utf-8
from ..define.id_enum import BedrockLavaDrill
from ..utils.structure_palette import GenerateSimpleStructureTemplate

IO_ENERGY = BedrockLavaDrill.IO_ENERGY
IO_FLUID1 = BedrockLavaDrill.IO_FLUID
FRAME = BedrockLavaDrill.FRAME

STRUCTURE_PATTERN_MAPPING = {
    "F": FRAME,
    "i": [FRAME, IO_FLUID1, IO_ENERGY],
    "e": [FRAME, IO_ENERGY],
}
STRUCTURE_PATTERN = {
    0: [
        "   F   ",
        "   F   ",
        "       ",
        "FF # FF",
        "       ",
        "   F   ",
        "   F   ",
    ],
    1: [
        "       ",
        "   F   ",
        "   F   ",
        " FF FF ",
        "   F   ",
        "   F   ",
        "       ",
    ],
    2: [
        "       ",
        "       ",
        "   e   ",
        "  eFe  ",
        "   e   ",
        "       ",
        "       ",
    ],
    3: [
        "       ",
        "       ",
        "       ",
        "   i   ",
        "       ",
        "       ",
        "       ",
    ],
}
STRUCTURE_REQUIRE_BLOCKS = {
    IO_ENERGY: 1,
    IO_FLUID1: 1,
}
DRILL_POWER = 1200
PUMP_POWER = 800
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    STRUCTURE_PATTERN_MAPPING,
    STRUCTURE_PATTERN,
    "#",
    require_blocks_count=STRUCTURE_REQUIRE_BLOCKS,
)
