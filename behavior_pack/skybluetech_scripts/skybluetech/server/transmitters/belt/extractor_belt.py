# coding=utf-8
from copy import deepcopy

from skybluetech_scripts.tooldelta.events.server import ServerBlockEntityTickEvent
from skybluetech_scripts.tooldelta.internal import GetServer
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.facing import DXYZ_FACING
from skybluetech_scripts.skybluetech.common.define.id_enum import TransmitBelt
from skybluetech_scripts.skybluetech.server.transmitters.item_pipe.logic import (
    _broadcast_pull_out,
)

from .container import get_container_slots, read_slot, write_slot
from .occupancy import ITEM_TYPE, get_belt_entities
from .utils import get_belt_direction

EXTRACT_INTERVAL_TICKS = 40
ITEM_SPAWN_OFFSET = 0.25
TICK_DATA_KEY = "extractor_belt_ticks"


def _extract_item(dim, belt_pos, container_pos, access_facing):
    # type: (int, tuple[int, int, int], tuple[int, int, int], int) -> None
    block_name, slots = get_container_slots(dim, container_pos, access_facing, False)
    for slot in slots:
        item, snapshot = read_slot(dim, container_pos, slot)
        if item is None:
            continue
        # 事件可以修改取出物品的嵌套数据，余量需在广播前独立保存。
        remainder = deepcopy(item)
        remainder.count -= 1
        piece = item.copy()
        piece.count = 1
        if not _broadcast_pull_out(dim, container_pos, slot, piece, block_name):
            continue
        # 源容器位于取货口一侧，沿该方向偏移生成位置。
        drop_pos = (
            belt_pos[0] + 0.5 + (container_pos[0] - belt_pos[0]) * ITEM_SPAWN_OFFSET,
            belt_pos[1] + 0.125,
            belt_pos[2] + 0.5 + (container_pos[2] - belt_pos[2]) * ITEM_SPAWN_OFFSET,
        )
        entity_id = GetServer().CreateEngineItemEntity(piece.marshal(), dim, drop_pos)
        if entity_id is None:
            return
        CF.CreateActorMotion(entity_id).SetMotion((0, 0, 0))
        # 只有创建成功才扣减；写回失败或源槽已改变时，撤销本次掉落物。
        if not write_slot(
            dim, container_pos, slot, block_name, snapshot,
            remainder if remainder.count > 0 else None,
        ):
            GetServer().DestroyEntity(entity_id)
        return


@ServerBlockEntityTickEvent.Listen()
def on_extractor_belt_tick(event):
    # type: (ServerBlockEntityTickEvent) -> None
    if event.blockName != TransmitBelt.EXTRACTOR:
        return
    pos = (event.posX, event.posY, event.posZ)
    data = CF.CreateBlockEntityData(LEVEL_ID).GetBlockEntityData(event.dimension, pos)
    if data is None:
        return
    ticks = (data[TICK_DATA_KEY] or 0) + 1
    data[TICK_DATA_KEY] = ticks % EXTRACT_INTERVAL_TICKS
    if ticks < EXTRACT_INTERVAL_TICKS:
        return
    if any(
        type_id == ITEM_TYPE
        for _, type_id in get_belt_entities(event.dimension, pos, event.blockName)
    ):
        return
    direction = get_belt_direction(event.dimension, pos)
    if direction is None:
        return
    dx, dz = direction
    container_pos = (pos[0] - dx, pos[1], pos[2] - dz)
    access_facing = DXYZ_FACING[(-dx, 0, -dz)]
    _extract_item(event.dimension, pos, container_pos, access_facing)
