# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum

from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID

from ....common.define.belt import BELT_STATUS, BeltState
from ....common.define.id_enum import TransmitBelt
from .utils import (
    FLAT_BELT_HEIGHT,
    INCLINE_TOP,
    get_direction_from_states,
    get_incline_height,
    is_in_belt_column,
    is_in_incline_lane,
)


EntityType = GetMinecraftEnum().EntityType
ITEM_TYPE = EntityType.ItemEntity


def _is_on_incline(entity_id, block_pos, pos, direction, rider):
    if rider is not None:
        return is_in_incline_lane(block_pos, pos, direction, rider[3])
    if not is_in_belt_column(block_pos, pos):
        return False
    size = CF.CreateCollisionBox(entity_id).GetSize()
    return (
        size is not None
        and pos[1] - block_pos[1] <= get_incline_height(block_pos, pos, direction, size[0] * 0.5) + FLAT_BELT_HEIGHT
    )


def get_belt_entities(dim, block_pos, block_name, incline_entities=None):
    x, y, z = block_pos
    direction = None
    if block_name == TransmitBelt.BELT:
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(block_pos, dim) or {}
        if states.get(BELT_STATUS) == BeltState.DIAGONAL_UP:
            direction = get_direction_from_states(states)

    if direction is None:
        low, high = block_pos, (x + 1, y + 0.5, z + 1)
        max_height = FLAT_BELT_HEIGHT
    else:
        dx, dz = direction
        max_height = INCLINE_TOP + FLAT_BELT_HEIGHT
        # 坡脚可能已接管脚点还在后方一格的实体。
        low = (x - max(dx, 0), y, z - max(dz, 0))
        high = (x + 1 - min(dx, 0), y + max_height, z + 1 - min(dz, 0))

    entities = CF.CreateGame(LEVEL_ID).GetEntitiesInSquareArea(None, low, high, dim)
    for entity_id in entities or ():
        pos = CF.CreatePos(entity_id).GetFootPos()
        if pos is None or not 0 <= pos[1] - y <= max_height:
            continue
        if direction is None:
            if not is_in_belt_column(block_pos, pos):
                continue
        else:
            rider = incline_entities.get(entity_id) if incline_entities is not None else None
            if rider is not None and rider[:3] != (dim, block_pos, direction):
                rider = None
            if not _is_on_incline(entity_id, block_pos, pos, direction, rider):
                continue
        entity_type = CF.CreateEngineType(entity_id).GetEngineType()
        if entity_type is not None:
            yield entity_id, entity_type & EntityType.TypeMask
