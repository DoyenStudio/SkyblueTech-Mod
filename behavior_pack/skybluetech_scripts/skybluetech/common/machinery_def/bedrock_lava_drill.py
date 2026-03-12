# coding=utf-8

IO_ENERGY = "skybluetech:drill_io_energy"
IO_FLUID1 = "skybluetech:drill_io_fluid"
IO_ITEM = "skybluetech:fermenter_io_item"
HEAVY_FRAME = "skybluetech:heavy_frame"
STRUCTURE_PATTERN_MAPPING = {
    "H": HEAVY_FRAME,
}
STRUCTURE_PATTERN = {
    0: [
        "   H   ",
        "       ",
        "       ",
        "H  #  H",
        "       ",
        "       ",
        "   H   ",
    ],
    1: [
        "       ",
        "   H   ",
        "       ",
        " H   H ",
        "       ",
        "   H   ",
        "       ",
    ],
    2: [
        "       ",
        "       ",
        "   H   ",
        "  H H  ",
        "   H   ",
        "       ",
        "       ",
    ],
}
STRUCTURE_REQUIRE_BLOCKS = {
    IO_ENERGY: 1,
    IO_FLUID1: 1,
}
