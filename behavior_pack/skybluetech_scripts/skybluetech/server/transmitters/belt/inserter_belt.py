# coding=utf-8
from mod_log import logger

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.events.server import ServerBlockEntityTickEvent
from skybluetech_scripts.tooldelta.internal import GetServer
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.skybluetech.common.define.facing import DXYZ_FACING
from skybluetech_scripts.skybluetech.common.define.id_enum import TransmitBelt
from skybluetech_scripts.skybluetech.server.transmitters.item_pipe.logic import (
    _broadcast_push_in,
    _calc_move_count,
)

from .container import get_container_slots, read_slot, write_slot
from .transmit_belt import INSERTER_STOP_OFFSET
from .utils import get_belt_direction, get_forward_offset

processing_entities = set()  # type: set[str]


def _same_stack(left, right):
    # type: (Item | None, Item) -> bool
    if left is None:
        return False
    return (
        left.id == right.id and left.newAuxValue == right.newAuxValue
        and left.count == right.count and left.userData == right.userData
        and (left.enchantData or []) == (right.enchantData or [])
        and (left.modEnchantData or []) == (right.modEnchantData or [])
        and left.extraId == right.extraId and left.customTips == right.customTips
        and (left.durability or 0) == (right.durability or 0)
    )


def _store_in_slot(dim, pos, slot, block_name, original, snapshot, entity_id, raw, count):
    # type: (int, tuple[int, int, int], int, str, Item | None, dict | None, str, dict, int) -> None
    server = GetServer()
    items = CF.CreateItem(LEVEL_ID)
    source = Item.from_dict(raw)
    target = original.copy() if original is not None else source.copy()
    target.count = (original.count if original is not None else 0) + count
    remainder_id = None
    if source.count > count:
        drop_pos = CF.CreatePos(entity_id).GetFootPos()
        if drop_pos is None:
            return
        remainder = source.copy()
        remainder.count -= count
        # 先在合堆半径之外创建余量，创建失败时保留原掉落物和容器。
        remainder_id = server.CreateEngineItemEntity(
            remainder.marshal(), dim, (drop_pos[0], drop_pos[1] + 8, drop_pos[2])
        )
        if remainder_id is None:
            return
        if not CF.CreatePos(remainder_id).SetPos(drop_pos):
            server.DestroyEntity(remainder_id)
            return
        CF.CreateActorMotion(remainder_id).SetMotion((0, 0, 0))
    if items.GetDroppedItem(entity_id, True) != raw or not write_slot(
        dim, pos, slot, block_name, snapshot, target
    ):
        if remainder_id is not None:
            server.DestroyEntity(remainder_id)
        return
    # 写入成功后才移除源实体；移除失败则仅回滚仍属于本次写入的槽位。
    if items.GetDroppedItem(entity_id, True) != raw or not server.DestroyEntity(entity_id):
        current, committed = read_slot(dim, pos, slot)
        matches_write = _same_stack(current, target)
        if not matches_write or not write_slot(
            dim, pos, slot, block_name, committed, original
        ):
            logger.error("[InserterBelt] Failed to roll back container slot: %s %s %s", dim, pos, slot)
        if remainder_id is not None:
            server.DestroyEntity(remainder_id)


def _insert_item(dim, pos, access_facing, entity_id, raw):
    # type: (int, tuple[int, int, int], int, str, dict) -> None
    block_name, slots = get_container_slots(dim, pos, access_facing, True)
    source = Item.from_dict(raw)
    for slot in slots:
        original, snapshot = read_slot(dim, pos, slot)
        count = _calc_move_count(source, original)
        if count <= 0:
            continue
        piece = source.copy()
        piece.count = count
        if not _broadcast_push_in(dim, pos, slot, piece, block_name):
            continue
        _store_in_slot(dim, pos, slot, block_name, original, snapshot, entity_id, raw, count)
        return


@ServerBlockEntityTickEvent.Listen()
def on_inserter_belt_tick(event):
    # type: (ServerBlockEntityTickEvent) -> None
    if event.blockName != TransmitBelt.INSERTER:
        return
    pos = (event.posX, event.posY, event.posZ)
    direction = get_belt_direction(event.dimension, pos)
    if direction is None:
        return
    dx, dz = direction
    entities = CF.CreateGame(LEVEL_ID).GetEntitiesInSquareArea(
        None, pos, (pos[0] + 1, pos[1] + 0.5, pos[2] + 1), event.dimension
    )
    for entity_id in entities or ():
        raw = CF.CreateItem(LEVEL_ID).GetDroppedItem(entity_id, True)
        if raw is None or raw["count"] <= 0:
            continue
        drop_pos = CF.CreatePos(entity_id).GetFootPos()
        if drop_pos is None or not (
            pos[0] <= drop_pos[0] < pos[0] + 1
            and pos[1] <= drop_pos[1] <= pos[1] + 0.125
            and pos[2] <= drop_pos[2] < pos[2] + 1
        ):
            continue
        # 每轮只处理找到的第一个掉落物，未到存货口或存不下也不改试后面的。
        forward_offset = get_forward_offset(pos, drop_pos, direction)
        if forward_offset < INSERTER_STOP_OFFSET - 0.0625 or entity_id in processing_entities:
            return
        processing_entities.add(entity_id)
        try:
            _insert_item(
                event.dimension, (pos[0] + dx, pos[1], pos[2] + dz),
                DXYZ_FACING[(dx, 0, dz)], entity_id, raw
            )
        finally:
            processing_entities.discard(entity_id)
        return
