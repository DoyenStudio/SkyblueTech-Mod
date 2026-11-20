# coding=utf-8
from skybluetech_scripts.tooldelta.events.server import (
    BlockRemoveServerEvent,
    ChunkLoadedServerEvent,
    EntityPlaceBlockAfterServerEvent,
    ServerPlaceBlockEntityEvent,
)
from skybluetech_scripts.tooldelta.general import ServerUninitCallback
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import ExecLater

from ....common.define.belt import BELTS, BELT_STATUS, OUTPUT_BELTS, BeltState
from ....common.define.facing import CARDINAL_DIRECTION_TO_DXZ, FACING_DXZ
from ....common.define.id_enum import TransmitBelt


DIRECTION_STATE = "minecraft:cardinal_direction"
_pending = set()  # type: set[tuple[int, int, int, int]]
_waiting_for_chunk = {}  # type: dict[tuple[int, int, int], set[tuple[int, int, int, int]]]


def _has_aligned_belt(block_info, block_state, dim, pos, direction):
    block = block_info.GetBlockNew(pos, dim)
    if block is None:
        return None
    if block.get("name") not in BELTS:
        return False
    states = block_state.GetBlockStates(pos, dim) or {}
    facing = states.get(DIRECTION_STATE)
    return facing == direction if facing is not None else None


def _shape_at(block_info, block_state, dim, pos, direction):
    x, y, z = pos
    dx, dz = CARDINAL_DIRECTION_TO_DXZ[direction]
    raised = _has_aligned_belt(
        block_info, block_state, dim, (x + dx, y + 1, z + dz), direction
    )
    if raised is not False:
        forward = _has_aligned_belt(
            block_info, block_state, dim, (x + dx, y, z + dz), direction
        )
        if forward is not True:
            # 前方区块尚未载入时保留之前的坡形。
            if raised is None or forward is None:
                return None
            return BeltState.DIAGONAL_UP

    shape = BeltState.STRAIGHT
    for sx, sz, corner in (
        (dz, -dx, BeltState.CORNER_LEFT),
        (-dz, dx, BeltState.CORNER_RIGHT),
    ):
        side = (x + sx, y, z + sz)
        block = block_info.GetBlockNew(side, dim) or {}
        if block.get("name") not in OUTPUT_BELTS:
            continue
        states = block_state.GetBlockStates(side, dim) or {}
        if states.get(BELT_STATUS) == BeltState.DIAGONAL_UP:
            continue
        if CARDINAL_DIRECTION_TO_DXZ.get(states.get(DIRECTION_STATE)) == (-sx, -sz):
            shape = corner
    return shape


def _refresh_belt(block_info, block_state, dim, x, y, z):
    pos = (x, y, z)
    block = block_info.GetBlockNew(pos, dim) or {}
    if block.get("name") != TransmitBelt.BELT:
        return
    states = block_state.GetBlockStates(pos, dim) or {}
    direction = states.get(DIRECTION_STATE)
    if direction not in CARDINAL_DIRECTION_TO_DXZ:
        return
    before = states.get(BELT_STATUS)
    after = _shape_at(block_info, block_state, dim, pos, direction)
    if after is None:
        dx, dz = CARDINAL_DIRECTION_TO_DXZ[direction]
        front_chunk = (dim, (x + dx) // 16, (z + dz) // 16)
        if front_chunk != (dim, x // 16, z // 16):
            _waiting_for_chunk.setdefault(front_chunk, set()).add((dim, x, y, z))
        return
    if before == after:
        return
    states[BELT_STATUS] = after
    if block_state.SetBlockStates(pos, states, dim) and BeltState.DIAGONAL_UP in (before, after):
        # 同高邻带只有在本带为平带时才能从本带接货。
        _queue_refresh((dim, x + dx, y, z + dz) for dx, dz in FACING_DXZ)


def _flush_pending():
    positions = tuple(_pending)
    _pending.clear()
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    block_state = CF.CreateBlockState(LEVEL_ID)
    for dim, x, y, z in positions:
        _refresh_belt(block_info, block_state, dim, x, y, z)


def _queue_refresh(positions):
    was_empty = not _pending
    _pending.update(positions)
    if was_empty and _pending:
        ExecLater(0, _flush_pending)


def _nearby_belts(dim, x, y, z):
    yield (dim, x, y, z)
    for dx, dz in FACING_DXZ:
        yield (dim, x + dx, y, z + dz)
        yield (dim, x + dx, y - 1, z + dz)


@EntityPlaceBlockAfterServerEvent.Listen()
def on_belt_placed(event):
    if event.fullName in BELTS:
        _queue_refresh(_nearby_belts(event.dimensionId, event.x, event.y, event.z))


@ServerPlaceBlockEntityEvent.Listen()
def on_belt_entity_placed(event):
    if event.blockName in BELTS:
        _queue_refresh(_nearby_belts(event.dimension, event.posX, event.posY, event.posZ))


@BlockRemoveServerEvent.Listen()
def on_belt_removed(event):
    if event.fullName in BELTS:
        # 等方块实际移除后重算，两种放置顺序和移除使用同一套规则。
        _queue_refresh(_nearby_belts(event.dimension, event.x, event.y, event.z))


@ChunkLoadedServerEvent.Listen()
def on_belts_loaded(event):
    chunk = (event.dimension, event.chunkPosX, event.chunkPosZ)
    _queue_refresh(_waiting_for_chunk.pop(chunk, ()))
    for block in event.blockEntities:
        if block["blockName"] in BELTS:
            _queue_refresh(_nearby_belts(
                event.dimension, block["posX"], block["posY"], block["posZ"]
            ))


@ServerUninitCallback()
def clear_pending_belts():
    _pending.clear()
    _waiting_for_chunk.clear()
