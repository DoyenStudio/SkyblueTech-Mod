# coding=utf-8
IO_ENERGY = "skybluetech:bedrock_lava_drill_io_energy"
IO_FLUID1 = "skybluetech:bedrock_lava_drill_io_fluid"
FRAME = "skybluetech:bedrock_lava_drill_frame"
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
