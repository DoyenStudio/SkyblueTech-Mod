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

BELTS = frozenset({
    TransmitBelt.BELT, TransmitBelt.EXTRACTOR, TransmitBelt.INSERTER,
    TransmitBelt.DETECTOR,
})
OUTPUT_BELTS = frozenset({
    TransmitBelt.BELT, TransmitBelt.EXTRACTOR, TransmitBelt.DETECTOR,
})


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


def get_motion_by_facing_str(cardinal_direction):
    # type: (str) -> tuple[float, float, float]
    dx, dz = CARDINAL_DIRECTION_TO_DXZ[cardinal_direction]
    return (dx * MOTION, 0, dz * MOTION)


def get_motion(dim, block_pos, entity_pos, block_name=TransmitBelt.BELT):
    # type: (int, tuple[int, int, int], tuple[float, float, float], str) -> tuple[float, float, float]
    blockstates = CF.CreateBlockState(LEVEL_ID).GetBlockStates(block_pos, dim)
    cardinal_direction = blockstates["minecraft:cardinal_direction"]  # type: str
    forward_motion = get_motion_by_facing_str(cardinal_direction)
    if block_name != TransmitBelt.BELT:
        return forward_motion

    axis = 0 if cardinal_direction in {"north", "south"} else 2
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
    incoming = CARDINAL_DIRECTION_TO_DXZ.get(
        neighbor_states.get("minecraft:cardinal_direction")
    )
    if incoming != (-dx, -dz):
        return forward_motion

    # 同时有左右输入时，按实体所在侧汇入，不能用单一转角状态选择方向。
    step = min(MOTION, abs(offset))
    return (-dx * step, 0, -dz * step)


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
        neighbor = (
            CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(neighbor_pos, event.dimension)
            or {}
        )
        if neighbor.get("name") not in OUTPUT_BELTS:
            continue
        neighbor_direction = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            neighbor_pos,
            event.dimension,
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
    pos = CF.CreatePos(event.entityId).GetFootPos()
    if pos is None:
        return
    x, y, z = pos
    # 碰撞盒可能横跨多条带，仅脚点所在格控制移动，避免相邻带争抢速度。
    if not (
        event.blockX <= x < event.blockX + 1
        and event.blockZ <= z < event.blockZ + 1
        and event.blockY <= y <= event.blockY + 0.125
    ):
        return
    dim = CF.CreateDimension(event.entityId).GetEntityDimensionId()
    motion = get_motion(
        dim, (event.blockX, event.blockY, event.blockZ), pos, event.blockName
    )
    motion_comp = CF.CreateActorMotion(event.entityId)
    entity_type = CF.CreateEngineType(event.entityId).GetEngineType()
    if entity_type is None:
        return
    type_id = entity_type & EntityType.TypeMask
    if event.blockName == TransmitBelt.INSERTER and type_id == EntityType.ItemEntity:
        # 沿输送方向计算距中心的偏移，掉落物在存货口前等待入库。
        forward_offset = get_forward_offset(
            (event.blockX, event.blockY, event.blockZ),
            (x, y, z),
            (motion[0] / MOTION, motion[2] / MOTION),
        )
        if forward_offset >= INSERTER_STOP_OFFSET - 1e-6:
            motion = (0, 0, 0)
    if type_id == (EntityType.Player & EntityType.TypeMask):
        player_motion = motion_comp.GetMotion()
        motion_comp.SetPlayerMotion(
            (
                motion[0],
                player_motion[1],
                motion[2],
            )
        )
    else:
        motion_comp.SetMotion(motion)
