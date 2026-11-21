# coding=utf-8
from ..define.id_enum import HEAVY_STEEL_MACHINE_BASE
from ..utils.structure_palette import GenerateSimpleStructureTemplate

ANCHOR = "skybluetech:chunk_anchor"
PORT = "skybluetech:chunk_anchor_energy_input_port"
CAPACITY = 64000
RADIUS = "st:anchor_radius"
STATUS = "st:anchor_status"
BEAM = "st:anchor_beam"
BEAM_OFF = 0
BEAM_BLUE = 1
BEAM_RED = 2
STRUCTURE_PALETTE = GenerateSimpleStructureTemplate(
    {"B": [HEAVY_STEEL_MACHINE_BASE, PORT]},
    {-1: ["BBB", "BBB", "BBB"], 0: ["   ", " # ", "   "]},
    require_blocks_count={PORT: 1},
)


def chunk_bounds(radius, x, z):
    cx, cz = x // 16, z // 16
    return (
        min(cx - radius, (x + STRUCTURE_PALETTE.min_x) // 16),
        min(cz - radius, (z + STRUCTURE_PALETTE.min_z) // 16),
        max(cx + radius, (x + STRUCTURE_PALETTE.max_x) // 16),
        max(cz + radius, (z + STRUCTURE_PALETTE.max_z) // 16),
    )


def chunk_count(bounds):
    min_x, min_z, max_x, max_z = bounds
    return (max_x - min_x + 1) * (max_z - min_z + 1)
