# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import (
    OnEntityInsideBlockServerEvent,
    ServerPlaceBlockEntityEvent,
)
from skybluetech_scripts.tooldelta.api.server import (
    GetEntityDimension,
    GetBlockNameAndAux,
    GetBlockCardinalFacing,
    GetBlockStates,
    GetFootPos,
    UpdateBlockStates,
    SetMotion,
)
from ...common.define.facing import CARDINAL_DIRECTION_TO_DXZ
from ...common.define.id_enum import TransmitBelt


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
    return {
        "north": (0, 0, -MOTION),
        "south": (0, 0, MOTION),
        "east": (MOTION, 0, 0),
        "west": (-MOTION, 0, 0),
    }[cardinal_direction]

def get_motion(dim, block_pos, entity_pos):
    # type: (int, tuple[int, int, int], tuple[float, float, float]) -> tuple[float, float, float]
    blockstates = GetBlockStates(dim, block_pos)
    cardinal_direction = blockstates["minecraft:cardinal_direction"] # type: str
    belt_state = blockstates["skybluetech:transmit_belt_status"] # type: str

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

@ServerPlaceBlockEntityEvent.Listen()
def onTransmitBeltPlaced(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if event.blockName != TransmitBelt.BELT:
        return
    cardinal_direction = GetBlockCardinalFacing(
        event.dimension, (event.posX, event.posY, event.posZ)
    )

    state = BeltState.STRAIGHT

    left_dir = get_left_direction(cardinal_direction)
    right_dir = get_right_direction(cardinal_direction)
    ldx, ldz = CARDINAL_DIRECTION_TO_DXZ[left_dir]
    rdx, rdz = CARDINAL_DIRECTION_TO_DXZ[right_dir]

    # 左边检测
    if (
        GetBlockNameAndAux(
            event.dimension, (event.posX + ldx, event.posY, event.posZ + ldz)
        )[0]
        == TransmitBelt.BELT
    ):
        lcardinal_direction = GetBlockCardinalFacing(
            event.dimension, (event.posX + ldx, event.posY, event.posZ + ldz)
        )
        if lcardinal_direction == right_dir:
            state = BeltState.CORNER_LEFT

    # 右边检测
    if (
        GetBlockNameAndAux(
            event.dimension, (event.posX + rdx, event.posY, event.posZ + rdz)
        )[0]
        == TransmitBelt.BELT
    ):
        rcardinal_direction = GetBlockCardinalFacing(
            event.dimension, (event.posX + rdx, event.posY, event.posZ + rdz)
        )
        if rcardinal_direction == left_dir:
            state = BeltState.CORNER_RIGHT


    UpdateBlockStates(
        event.dimension,
        (event.posX, event.posY, event.posZ),
        {"skybluetech:transmit_belt_status": state},
    )

@OnEntityInsideBlockServerEvent.Listen()
def onEntityInsideBlock(event):
    # type: (OnEntityInsideBlockServerEvent) -> None
    if event.blockName != TransmitBelt.BELT:
        return
    x, y, z = GetFootPos(event.entityId)
    if y % 1.0 > 0.125:
        return
    dim = GetEntityDimension(event.entityId)
    SetMotion(event.entityId, get_motion(dim, (event.blockX, event.blockY, event.blockZ), (x, y, z)))
