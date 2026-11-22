# coding=utf-8
from collections import deque
from mod_log import logger

from skybluetech_scripts.tooldelta.events.server import OnSimTickServerEvent
from skybluetech_scripts.tooldelta.general import ServerUninitCallback
from skybluetech_scripts.tooldelta.internal import GetServer
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID


REFRESH_AGE = 5900
CHECK_INTERVAL_TICKS = 20
_checked_items = set()
_expiring_checks = deque(set() for _ in range(CHECK_INTERVAL_TICKS))


@OnSimTickServerEvent.Listen()
def _expire_item_checks(_event):
    bucket = _expiring_checks.popleft()
    _checked_items.difference_update(bucket)
    bucket.clear()
    _expiring_checks.append(bucket)


def refresh_belt_item(entity_id, dim):
    # type: (str, int) -> str
    if entity_id in _checked_items:
        return entity_id
    _checked_items.add(entity_id)
    _expiring_checks[-1].add(entity_id)

    nbt = CF.CreateEntityDefinitions(entity_id).GetEntityNBTTags()
    age = nbt.get("Age") if nbt else None
    if not age or age.get("__value__", 0) < REFRESH_AGE:
        return entity_id

    items = CF.CreateItem(LEVEL_ID)
    original = items.GetDroppedItem(entity_id, True)
    pos = CF.CreatePos(entity_id).GetFootPos()
    if original is None or pos is None:
        return entity_id

    age["__value__"] = 0
    nbt.pop("UniqueID", None)
    server = GetServer()
    replacement = server.CreateEngineEntityByNBT(nbt, None, None, dim)
    if replacement is None or replacement == entity_id:
        return entity_id

    # 替代品写入成功且原物品仍在原位时才提交替换。
    if (
        items.GetDroppedItem(replacement, True) == original
        and CF.CreatePos(replacement).GetFootPos() == pos
        and items.GetDroppedItem(entity_id, True) == original
        and CF.CreatePos(entity_id).GetFootPos() == pos
        and server.DestroyEntity(entity_id)
    ):
        _checked_items.add(replacement)
        _expiring_checks[-1].add(replacement)
        return replacement

    if not server.DestroyEntity(replacement):
        logger.error("[Belt] Failed to remove replacement drop: %s", replacement)
    return entity_id


@ServerUninitCallback()
def _clear_item_checks():
    _checked_items.clear()
    for bucket in _expiring_checks:
        bucket.clear()
