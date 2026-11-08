# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.facing import CARDINAL_DIRECTION_TO_DXZ


def get_belt_direction(dim, pos):
    # type: (int, tuple[int, int, int]) -> tuple[int, int] | None
    states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(pos, dim) or {}
    return CARDINAL_DIRECTION_TO_DXZ.get(states.get("minecraft:cardinal_direction"))


def get_forward_offset(block_pos, entity_pos, direction):
    # type: (tuple[int, int, int], tuple[float, float, float], tuple[float, float]) -> float
    dx, dz = direction
    return (entity_pos[0] - block_pos[0] - 0.5) * dx + (entity_pos[2] - block_pos[2] - 0.5) * dz
