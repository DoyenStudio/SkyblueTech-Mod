# coding=utf-8
from skybluetech_scripts.skybluetech.common.define.id_enum import (
    CommonLiquid,
    SeawaterReservoir,
)
from skybluetech_scripts.skybluetech.common.utils.structure_palette import (
    GenerateSimpleStructureTemplate,
    StructureBlockPalette,
)

CONTROLLER = SeawaterReservoir.CONTROLLER
IO_ENERGY = SeawaterReservoir.IO_ENERGY
MAX_FLUID_VOLUME = 4000
STORE_RF_MAX = 10000
RUNNING_POWER = 80
OUTPUT_FLUID = CommonLiquid.DILUTE_BRINE
MAX_OUTPUT_PER_TICK = 1000.0
WATER_SCAN_RADIUS = 30
WATER_SCAN_HEIGHT = 20
WATER_SCAN_VOLUME = (WATER_SCAN_RADIUS * 2 + 1) ** 2 * WATER_SCAN_HEIGHT
MIN_WATER_RATIO = 0.3
FULL_SPEED_WATER_RATIO = 0.6
K_WATER_BLOCK_COUNT = "st:water_block_count"


def get_output_per_tick(water_block_count):
    # type: (int) -> float
    min_count = WATER_SCAN_VOLUME * MIN_WATER_RATIO
    full_speed_count = WATER_SCAN_VOLUME * FULL_SPEED_WATER_RATIO
    if water_block_count <= min_count:
        return 0.0
    if water_block_count >= full_speed_count:
        return MAX_OUTPUT_PER_TICK
    return (
        MAX_OUTPUT_PER_TICK
        * (water_block_count - min_count)
        / (full_speed_count - min_count)
    )


STRUCTURE_PALETTE_DICT = {
    0: [
        "SSSSSSS",
        "SsssssS",
        "SssessS",
        "Sse#esS",
        "SssessS",
        "SsssssS",
        "SSSSSSS",
    ],
    -6: [
        "SSSSSSS",
        "SsssssS",
        "SsssssS",
        "SsssssS",
        "SsssssS",
        "SsssssS",
        "SSSSSSS",
    ],
}
for i in range(1, 6):
    STRUCTURE_PALETTE_DICT[-i] = [
        "SCCCCCS",
        "CWWWWWC",
        "CWWWWWC",
        "CWWWWWC",
        "CWWWWWC",
        "CWWWWWC",
        "SCCCCCS",
    ]

STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    {
        "S": "minecraft:stone_bricks",
        "s": ["minecraft:stone_bricks", "minecraft:glass"],
        "e": [IO_ENERGY, "minecraft:stone_bricks", "minecraft:glass"],
        "W": "minecraft:water",
        "C": "minecraft:waxed_copper_grate",
    },
    STRUCTURE_PALETTE_DICT,
    "#",
    require_blocks_count={IO_ENERGY: 1},
)
