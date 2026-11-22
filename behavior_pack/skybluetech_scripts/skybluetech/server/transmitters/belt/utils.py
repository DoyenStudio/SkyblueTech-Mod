# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.facing import CARDINAL_DIRECTION_TO_DXZ


MOTION = 0.05
FLAT_BELT_HEIGHT = 0.125
INCLINE_TOP = 1.1125


def get_direction_from_states(states):
    return CARDINAL_DIRECTION_TO_DXZ.get(states.get("minecraft:cardinal_direction"))


def get_belt_direction(dim, pos):
    # type: (int, tuple[int, int, int]) -> tuple[int, int] | None
    states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(pos, dim) or {}
    return get_direction_from_states(states)


def get_forward_offset(block_pos, entity_pos, direction):
    # type: (tuple[int, int, int], tuple[float, float, float], tuple[float, float]) -> float
    dx, dz = direction
    return (entity_pos[0] - block_pos[0] - 0.5) * dx + (entity_pos[2] - block_pos[2] - 0.5) * dz


def is_in_belt_column(block_pos, pos):
    return (
        block_pos[0] <= pos[0] < block_pos[0] + 1
        and block_pos[2] <= pos[2] < block_pos[2] + 1
    )


def is_in_incline_lane(block_pos, pos, direction, half_width):
    if is_in_belt_column(block_pos, pos):
        return True
    # 碰撞盒前缘先碰到坡脚，实体脚点此时仍在后方一格。
    axis = 2 if direction[0] else 0
    if not block_pos[axis] <= pos[axis] < block_pos[axis] + 1:
        return False
    progress = get_forward_offset(block_pos, pos, direction) + 0.5
    return -min(half_width + 0.01, 1) <= progress <= 0


def get_incline_height(block_pos, pos, direction, half_width):
    progress = get_forward_offset(block_pos, pos, direction) + 0.5
    # 先抬高碰撞盒的前缘，避免在坡顶被上一层传送带的边缘卡住。
    return min(INCLINE_TOP, 0.0625 + progress + half_width + MOTION)
