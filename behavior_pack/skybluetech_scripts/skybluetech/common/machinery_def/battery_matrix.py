# coding=utf-8
CORE = "skybluetech:battery_matrix_core"
FRAME = "skybluetech:battery_matrix_frame"
IO_ENERGY_INPUT = "skybluetech:battery_matrix_io_energy1"
IO_ENERGY_OUTPUT = "skybluetech:battery_matrix_io_energy2"
STRUCTURE_PATTERN_MAPPING = {
    "F": FRAME,
    "f": [FRAME, IO_ENERGY_INPUT, IO_ENERGY_OUTPUT],
    "C": CORE,
}
STRUCTURE_PATTERN = {
    -1: [
        "FfF",
        "fff",
        "FfF",
    ],
    0: [
        "f#f",
        "fCf",
        "fff",
    ],
    1: [
        "FfF",
        "fff",
        "FfF",
    ],
}
STRUCTURE_REQUIRE_BLOCKS = {
    IO_ENERGY_INPUT: 1,
    IO_ENERGY_OUTPUT: 1,
    CORE: 1,
}
