# coding=utf-8
"""通过自定义方块状态维护电池仓和基岩熔岩钻各自的六向连接。"""

from skybluetech_scripts.tooldelta.events.server import (
    BlockNeighborChangedServerEvent,
    BlockRemoveServerEvent,
    EntityPlaceBlockAfterServerEvent,
    ServerPlaceBlockEntityEvent,
)
from skybluetech_scripts.tooldelta.events.server.world import (
    ChunkAcquireDiscardedServerEvent,
    ChunkLoadedServerEvent,
)
from skybluetech_scripts.tooldelta.general import ServerUninitCallback
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.timer import ExecLater
from skybluetech_scripts.skybluetech.common.define.id_enum.multi_block_structure import (
    BatteryMatrix,
    BedrockLavaDrill,
)


SHELL_GROUPS = (
    frozenset((
        BatteryMatrix.FRAME,
        BatteryMatrix.CONTROLLER,
        BatteryMatrix.IO_ENERGY_INPUT,
        BatteryMatrix.IO_ENERGY_OUTPUT,
    )),
    frozenset((
        BedrockLavaDrill.FRAME,
        BedrockLavaDrill.CONTROLLER,
        BedrockLavaDrill.IO_ENERGY,
        BedrockLavaDrill.IO_FLUID,
    )),
)
# 共用事件和加载索引，但不同机器的外壳不能互相连接。
SHELL_GROUP_BY_BLOCK = dict(
    (block_name, group) for group in SHELL_GROUPS for block_name in group
)
SHELL_BLOCKS = frozenset(SHELL_GROUP_BY_BLOCK)
NEIGHBOR_STATES = (
    ((0, 1, 0), "skybluetech:connection_up"),
    ((0, -1, 0), "skybluetech:connection_down"),
    ((0, 0, -1), "skybluetech:connection_north"),
    ((0, 0, 1), "skybluetech:connection_south"),
    ((-1, 0, 0), "skybluetech:connection_west"),
    ((1, 0, 0), "skybluetech:connection_east"),
)
_pending_positions = set()  # type: set[tuple[int, int, int, int]]
# 只索引已加载的外壳，区块加载时修复边界邻接，无需遍历区块内所有方块。
_loaded_shells = {}  # type: dict[tuple[int, int, int], set[tuple[int, int, int]]]


def _refresh_connections(dimension, x, y, z):
    # type: (int, int, int, int) -> None
    pos = (x, y, z)
    block_info = CF.CreateBlockInfo(LEVEL_ID)
    block = block_info.GetBlockNew(pos, dimension)
    if block is None:
        return
    chunk_key = (dimension, x // 16, z // 16)
    shell_group = SHELL_GROUP_BY_BLOCK.get(block.get("name"))
    if shell_group is None:
        positions = _loaded_shells.get(chunk_key)
        if positions is not None:
            positions.discard(pos)
            if not positions:
                _loaded_shells.pop(chunk_key, None)
        return
    _loaded_shells.setdefault(chunk_key, set()).add(pos)
    block_state = CF.CreateBlockState(LEVEL_ID)
    states = block_state.GetBlockStates(pos, dimension)
    if states is None:
        return
    changed = False
    for (dx, dy, dz), state_name in NEIGHBOR_STATES:
        neighbor = block_info.GetBlockNew((x + dx, y + dy, z + dz), dimension)
        # 读取失败不是空气，不覆盖尚未加载/不可读取位置的已有状态。
        if neighbor is None:
            continue
        connected = neighbor.get("name") in shell_group
        if states.get(state_name) != connected:
            states[state_name] = connected
            changed = True
    if changed:
        # 仅更新六向连接，原样保留朝向与 active 等其他状态。
        block_state.SetBlockStates(pos, states, dimension)


def _flush_pending():
    # type: () -> None
    positions = tuple(_pending_positions)
    _pending_positions.clear()
    for dimension, x, y, z in positions:
        _refresh_connections(dimension, x, y, z)


def _queue_refresh(dimension, x, y, z):
    # type: (int, int, int, int) -> None
    was_empty = not _pending_positions
    _pending_positions.add((dimension, x, y, z))
    if was_empty:
        ExecLater(0, _flush_pending)


def _queue_neighborhood(dimension, x, y, z):
    # type: (int, int, int, int) -> None
    _queue_refresh(dimension, x, y, z)
    for (dx, dy, dz), _ in NEIGHBOR_STATES:
        _queue_refresh(dimension, x + dx, y + dy, z + dz)


@EntityPlaceBlockAfterServerEvent.Listen()
def on_entity_placed(event):
    # type: (EntityPlaceBlockAfterServerEvent) -> None
    if event.fullName in SHELL_BLOCKS:
        _queue_neighborhood(event.dimensionId, event.x, event.y, event.z)


@ServerPlaceBlockEntityEvent.Listen()
def on_block_entity_placed(event):
    # type: (ServerPlaceBlockEntityEvent) -> None
    if event.blockName in SHELL_BLOCKS:
        _queue_neighborhood(event.dimension, event.posX, event.posY, event.posZ)


@BlockNeighborChangedServerEvent.Listen()
def on_neighbor_changed(event):
    # type: (BlockNeighborChangedServerEvent) -> None
    if event.blockName not in SHELL_BLOCKS:
        return
    # 邻块仅改变状态不会改变能否连接，避免状态写入相互触发。
    if event.fromBlockName == event.toBlockName:
        return
    distance = (
        abs(event.neighborPosX - event.posX)
        + abs(event.neighborPosY - event.posY)
        + abs(event.neighborPosZ - event.posZ)
    )
    if distance != 1:
        return
    _queue_refresh(event.dimensionId, event.posX, event.posY, event.posZ)


@BlockRemoveServerEvent.Listen()
def on_block_removed(event):
    # type: (BlockRemoveServerEvent) -> None
    if event.fullName in SHELL_BLOCKS:
        # 同步移除回调仍能读到旧方块；下一 tick 按现状更新，也兼容快速重放。
        _queue_neighborhood(event.dimension, event.x, event.y, event.z)


def _queue_loaded_positions(dimension, positions):
    # type: (int, tuple[tuple[int, int, int], ...]) -> None
    for x, y, z in positions:
        _queue_refresh(dimension, x, y, z)


@ChunkLoadedServerEvent.Listen()
def on_chunk_loaded(event):
    # type: (ChunkLoadedServerEvent) -> None
    positions = set(
        (block["posX"], block["posY"], block["posZ"])
        for block in event.blockEntities
        if block["blockName"] in SHELL_BLOCKS
    )
    chunk_x, chunk_z = event.chunkPosX, event.chunkPosZ
    chunk_key = (event.dimension, chunk_x, chunk_z)
    if positions:
        _loaded_shells[chunk_key] = positions.copy()
    else:
        _loaded_shells.pop(chunk_key, None)
    # 即使新加载区块没有外壳，也要修复邻区块面向它的边界外壳。
    for dx, dz, axis, boundary in (
        (-1, 0, 0, chunk_x * 16 - 1),
        (1, 0, 0, (chunk_x + 1) * 16),
        (0, -1, 2, chunk_z * 16 - 1),
        (0, 1, 2, (chunk_z + 1) * 16),
    ):
        neighbor_key = (event.dimension, chunk_x + dx, chunk_z + dz)
        for pos in _loaded_shells.get(neighbor_key, ()):
            if pos[axis] == boundary:
                positions.add(pos)
    if positions:
        # 与现有管线加载修复一致，稍后读取已加载的方块；无需扫描整个区块。
        ExecLater(1, _queue_loaded_positions, event.dimension, tuple(positions))


@ChunkAcquireDiscardedServerEvent.Listen()
def on_chunk_unloaded(event):
    # type: (ChunkAcquireDiscardedServerEvent) -> None
    _loaded_shells.pop((event.dimension, event.chunkPosX, event.chunkPosZ), None)


@ServerUninitCallback()
def on_server_uninit():
    # type: () -> None
    _pending_positions.clear()
    _loaded_shells.clear()
