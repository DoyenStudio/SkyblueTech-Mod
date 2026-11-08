# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.events.server import (
    OnEntityInsideBlockServerEvent,
    ServerPlaceBlockEntityEvent,
)

from ....common.define.facing import CARDINAL_DIRECTION_TO_DXZ
from ....common.define.id_enum import TransmitBelt
from .utils import get_forward_offset

EntityType = GetMinecraftEnum().EntityType

BELTS = frozenset({TransmitBelt.BELT, TransmitBelt.EXTRACTOR, TransmitBelt.INSERTER})
OUTPUT_BELTS = frozenset({TransmitBelt.BELT, TransmitBelt.EXTRACTOR})


class BeltState:
    STRAIGHT = "straight"
    CORNER_LEFT = "corner_left"
    CORNER_RIGHT = "corner_right"
    DIAGONAL_UP = "diagonal_up"
    DIAGONAL_DOWN = "diagonal_down"


def get_right_direction(facing):
    # type: (str) -> str
    return {"north": "east", "east": "south", "south": "west", "west": "north"}[facing]


def get_left_direction(facing):
    # type: (str) -> str
    return {"north": "west", "west": "south", "south": "east", "east": "north"}[facing]


def is_middle(num):
    # type: (float) -> bool
    return abs(num % 1.0 - 0.5) < 0.0625


def get_motion_by_facing_str(cardinal_direction):
    # type: (str) -> tuple[float, float, float]
    dx, dz = CARDINAL_DIRECTION_TO_DXZ[cardinal_direction]
    return (dx * MOTION, 0, dz * MOTION)


def get_motion(dim, block_pos, entity_pos):
    # type: (int, tuple[int, int, int], tuple[float, float, float]) -> tuple[float, float, float]
    blockstates = CF.CreateBlockState(LEVEL_ID).GetBlockStates(block_pos, dim)
    cardinal_direction = blockstates["minecraft:cardinal_direction"]  # type: str
    belt_state = blockstates.get("skybluetech:transmit_belt_status", BeltState.STRAIGHT)  # type: str

    if belt_state == BeltState.STRAIGHT:
        return get_motion_by_facing_str(cardinal_direction)

    elif belt_state in {BeltState.CORNER_LEFT, BeltState.CORNER_RIGHT}:
        if cardinal_direction in {"north", "south"}:
            is_mid = is_middle(entity_pos[0])
        else:
            is_mid = is_middle(entity_pos[2])
        if is_mid:
            return get_motion_by_facing_str(cardinal_direction)
        else:
            if belt_state == BeltState.CORNER_LEFT:
                # print "GOTO", get_right_direction(cardinal_direction)
                return get_motion_by_facing_str(get_right_direction(cardinal_direction))
            elif belt_state == BeltState.CORNER_RIGHT:
                # print "GOTO", get_left_direction(cardinal_direction)
                return get_motion_by_facing_str(get_left_direction(cardinal_direction))
            else:
                raise ValueError("Error belt state support")

    else:
        raise ValueError("Unknown transmitelt state: " + belt_state)


MOTION = 0.05
INSERTER_STOP_OFFSET = 0.25


@ServerPlaceBlockEntityEvent.Listen()
def on_belt_placed(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if event.blockName != TransmitBelt.BELT:
        return
    cardinal_direction = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
        (event.posX, event.posY, event.posZ),
        event.dimension,
    )["minecraft:cardinal_direction"]

    state = BeltState.STRAIGHT

    left_dir = get_left_direction(cardinal_direction)
    right_dir = get_right_direction(cardinal_direction)
    for side, incoming, corner_state in (
        (left_dir, right_dir, BeltState.CORNER_LEFT),
        (right_dir, left_dir, BeltState.CORNER_RIGHT),
    ):
        dx, dz = CARDINAL_DIRECTION_TO_DXZ[side]
        neighbor_pos = (event.posX + dx, event.posY, event.posZ + dz)
        neighbor = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(neighbor_pos, event.dimension) or {}
        if neighbor.get("name") not in OUTPUT_BELTS:
            continue
        neighbor_direction = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            neighbor_pos, event.dimension,
        )["minecraft:cardinal_direction"]
        if neighbor_direction == incoming:
            state = corner_state

    _block_states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
        (event.posX, event.posY, event.posZ),
        event.dimension,
    )
    if _block_states is not None:
        _block_states.update({"skybluetech:transmit_belt_status": state})
        CF.CreateBlockState(LEVEL_ID).SetBlockStates(
            (event.posX, event.posY, event.posZ),
            _block_states,
            event.dimension,
        )


@OnEntityInsideBlockServerEvent.Listen()
def _on_entity_inside_belt(event):
    # type: (OnEntityInsideBlockServerEvent) -> None
    if event.blockName not in BELTS:
        return
    x, y, z = CF.CreatePos(event.entityId).GetFootPos()
    if y % 1.0 > 0.125:
        return
    dim = CF.CreateDimension(event.entityId).GetEntityDimensionId()
    motion = get_motion(dim, (event.blockX, event.blockY, event.blockZ), (x, y, z))
    motion_comp = CF.CreateActorMotion(event.entityId)
    entity_type = CF.CreateEngineType(event.entityId).GetEngineType()
    if entity_type is None:
        return
    type_id = entity_type & EntityType.TypeMask
    if event.blockName == TransmitBelt.INSERTER and type_id == EntityType.ItemEntity:
        # 沿输送方向计算距中心的偏移，掉落物在存货口前等待入库。
        forward_offset = get_forward_offset(
            (event.blockX, event.blockY, event.blockZ), (x, y, z),
            (motion[0] / MOTION, motion[2] / MOTION),
        )
        if forward_offset >= INSERTER_STOP_OFFSET - 1e-6:
            motion = (0, 0, 0)
    if type_id == (EntityType.Player & EntityType.TypeMask):
        motion_comp.SetPlayerMotion(motion)
    else:
        motion_comp.SetMotion(motion)
