# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.server import (
    OnEntityInsideBlockServerEvent,
    OnScriptTickServer,
)
from skybluetech_scripts.tooldelta.general import ServerUninitCallback

from ....common.define.belt import BELTS, BELT_STATUS, OUTPUT_BELTS, BeltState
from ....common.define.id_enum import TransmitBelt
from .item_lifetime import refresh_belt_item
from .occupancy import EntityType, ITEM_TYPE, get_belt_entities
from .utils import (
    FLAT_BELT_HEIGHT,
    INCLINE_TOP,
    MOTION,
    get_direction_from_states,
    get_forward_offset,
    get_incline_height,
    is_in_belt_column,
    is_in_incline_lane,
)

PLAYER_TYPE = EntityType.Player & EntityType.TypeMask

INSERTER_STOP_OFFSET = 0.25
OUTLET_STOP_OFFSET = 0.5 - 0.03125
MAX_INCLINE_LIFT = 0.25
incline_entities = {}


def _is_belt_occupied(dim, block_pos, block_name, entity_id):
    return any(
        other_id != entity_id
        for other_id, _ in get_belt_entities(dim, block_pos, block_name, incline_entities)
    )


def _is_front_belt_occupied(dim, block_pos, direction, rise, entity_id):
    x, y, z = block_pos
    dx, dz = direction
    next_pos = (x + dx, y + rise, z + dz)
    next_block = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(next_pos, dim) or {}
    next_name = next_block.get("name")
    return next_name in BELTS and _is_belt_occupied(dim, next_pos, next_name, entity_id)


def _get_forward_speed(dim, block_pos, pos, direction, rise, entity_id):
    # 让脚点停在本带末端，避免下一段提前接手。
    remaining = OUTLET_STOP_OFFSET - get_forward_offset(block_pos, pos, direction)
    if remaining >= MOTION or not _is_front_belt_occupied(dim, block_pos, direction, rise, entity_id):
        return MOTION
    return max(0, remaining)


def _is_closed_incline_side(dim, block_pos, direction):
    dx, dz = direction
    next_pos = (block_pos[0] + dx, block_pos[1], block_pos[2] + dz)
    next_block = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(next_pos, dim) or {}
    if next_block.get("name") != TransmitBelt.BELT:
        return False
    next_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(next_pos, dim) or {}
    if next_states.get(BELT_STATUS) != BeltState.DIAGONAL_UP:
        return False
    next_direction = get_direction_from_states(next_states)
    return next_direction is not None and dx * next_direction[0] + dz * next_direction[1] == 0


def _get_flat_motion(dim, block_pos, entity_pos, direction, block_name, speed):
    dx, dz = direction
    forward_motion = (dx * speed, 0, dz * speed)
    if (
        get_forward_offset(block_pos, entity_pos, direction) >= 0.5 - MOTION - 1e-4
        and _is_closed_incline_side(dim, block_pos, direction)
    ):
        return (0, 0, 0)
    if block_name != TransmitBelt.BELT:
        return forward_motion

    axis = 2 if dx else 0
    offset = entity_pos[axis] - block_pos[axis] - 0.5
    if abs(offset) <= 0.0625:
        return forward_motion

    side = 1 if offset > 0 else -1
    dx, dz = (side, 0) if axis == 0 else (0, side)
    neighbor_pos = (block_pos[0] + dx, block_pos[1], block_pos[2] + dz)
    neighbor = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(neighbor_pos, dim) or {}
    if neighbor.get("name") not in OUTPUT_BELTS:
        return forward_motion
    neighbor_states = (
        CF.CreateBlockState(LEVEL_ID).GetBlockStates(neighbor_pos, dim) or {}
    )
    if (
        neighbor_states.get(BELT_STATUS) == BeltState.DIAGONAL_UP
        or get_direction_from_states(neighbor_states) != (-dx, -dz)
    ):
        return forward_motion

    # 同时有左右输入时，按实体所在侧汇入，不能用单一转角状态选择方向。
    step = min(MOTION, abs(offset))
    return (-dx * step, 0, -dz * step)


def _apply_motion(entity_id, type_id, motion, preserve_player_y=False):
    motion_comp = CF.CreateActorMotion(entity_id)
    if type_id == PLAYER_TYPE:
        if preserve_player_y:
            motion = (motion[0], motion_comp.GetMotion()[1], motion[2])
        motion_comp.SetPlayerMotion(motion)
    else:
        motion_comp.SetMotion(motion)


@OnScriptTickServer.Listen()
def _tick_incline_entities(_event):
    # 脚点升出源方块后不再触发 OnEntityInsideBlock，继续推到脚点进入上层带所在列。
    for entity_id, rider in tuple(incline_entities.items()):
        dim, block_pos, direction, half_width, type_id = rider
        pos = CF.CreatePos(entity_id).GetFootPos()
        if not (
            pos is not None
            and is_in_incline_lane(block_pos, pos, direction, half_width)
            and 0 <= pos[1] - block_pos[1] <= INCLINE_TOP + FLAT_BELT_HEIGHT
            and CF.CreateDimension(entity_id).GetEntityDimensionId() == dim
        ):
            del incline_entities[entity_id]
            continue
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(block_pos, dim) or {}
        if states.get(BELT_STATUS) != BeltState.DIAGONAL_UP or get_direction_from_states(states) != direction:
            del incline_entities[entity_id]
            continue
        if type_id == ITEM_TYPE:
            current_id = refresh_belt_item(entity_id, dim)
            if current_id != entity_id:
                del incline_entities[entity_id]
                incline_entities[current_id] = rider
                entity_id = current_id
        height = get_incline_height(block_pos, pos, direction, half_width)
        # 实体各自的重力在移动阶段扣减纵向速度。
        gravity = 0.05 if type_id == ITEM_TYPE else 0.09
        if type_id == PLAYER_TYPE and CF.CreateFly(entity_id).IsPlayerFlying():
            gravity = 0
        lift = max(0, min(MAX_INCLINE_LIFT, block_pos[1] + height - pos[1] + gravity))
        dx, dz = direction
        speed = _get_forward_speed(dim, block_pos, pos, direction, 1, entity_id)
        _apply_motion(entity_id, type_id, (dx * speed, lift, dz * speed))


@OnEntityInsideBlockServerEvent.Listen()
def _on_entity_inside_belt(event):
    # type: (OnEntityInsideBlockServerEvent) -> None
    if event.blockName not in BELTS:
        return
    pos = CF.CreatePos(event.entityId).GetFootPos()
    if pos is None:
        return
    block_pos = (event.blockX, event.blockY, event.blockZ)
    height = pos[1] - event.blockY
    if not 0 <= height < 1:
        return
    in_column = is_in_belt_column(block_pos, pos)
    if event.blockName != TransmitBelt.BELT and (not in_column or height > FLAT_BELT_HEIGHT):
        return
    dim = CF.CreateDimension(event.entityId).GetEntityDimensionId()
    riding = incline_entities.get(event.entityId)
    if riding is not None and riding[:2] == (dim, block_pos):
        return
    states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(block_pos, dim) or {}
    direction = get_direction_from_states(states)
    if direction is None:
        return
    is_incline = states.get(BELT_STATUS) == BeltState.DIAGONAL_UP
    if not is_incline:
        # 平带只控制脚点所在格，并把坡脚已接手的实体交给坡带。
        if not in_column or height > FLAT_BELT_HEIGHT:
            return
        if riding is not None and riding[0] == dim:
            _, incline_pos, incline_direction, half_width, _ = riding
            if is_in_incline_lane(incline_pos, pos, incline_direction, half_width):
                return
    entity_type = CF.CreateEngineType(event.entityId).GetEngineType()
    if entity_type is None:
        return
    type_id = entity_type & EntityType.TypeMask
    if is_incline:
        size = CF.CreateCollisionBox(event.entityId).GetSize()
        if size is None:
            return
        half_width = size[0] * 0.5
        if (
            is_in_incline_lane(block_pos, pos, direction, half_width)
            and height <= get_incline_height(block_pos, pos, direction, half_width) + FLAT_BELT_HEIGHT
            and (in_column or not _is_belt_occupied(dim, block_pos, event.blockName, event.entityId))
        ):
            incline_entities[event.entityId] = (dim, block_pos, direction, half_width, type_id)
        return

    entity_id = event.entityId
    if type_id == ITEM_TYPE:
        entity_id = refresh_belt_item(entity_id, dim)
    speed = _get_forward_speed(dim, block_pos, pos, direction, 0, entity_id)
    motion = _get_flat_motion(dim, block_pos, pos, direction, event.blockName, speed)
    if event.blockName == TransmitBelt.INSERTER and type_id == ITEM_TYPE:
        # 沿输送方向计算距中心的偏移，掉落物在存货口前等待入库。
        forward_offset = get_forward_offset(block_pos, pos, direction)
        if forward_offset >= INSERTER_STOP_OFFSET - 1e-6:
            motion = (0, 0, 0)
    _apply_motion(entity_id, type_id, motion, preserve_player_y=True)


@ServerUninitCallback()
def _clear_incline_entities():
    incline_entities.clear()
