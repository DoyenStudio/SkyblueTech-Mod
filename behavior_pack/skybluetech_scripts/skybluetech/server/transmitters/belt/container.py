# coding=utf-8
from copy import deepcopy

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.nbt import Byte
from skybluetech_scripts.tooldelta.utils.py_comp import py2_xrange
from skybluetech_scripts.skybluetech.server.transmitters.constants import CHEST_CONTAINERS
from skybluetech_scripts.skybluetech.server.transmitters.item_pipe.logic import (
    InvalidateContainerCaches,
    _filter_machine_slots_for_access,
)
from skybluetech_scripts.skybluetech.server.transmitters.item_pipe.nbt_utils import (
    _find_slot_entry,
    _get_container_nbt,
    _item_to_nbt_entry,
    _nbt_entry_to_item,
)


def get_container_slots(dim, pos, access_facing, is_input):
    # type: (int, tuple[int, int, int], int, bool) -> tuple[str, tuple[int, ...]]
    size = CF.CreateItem(LEVEL_ID).GetContainerSize(pos, dim)
    if size is None or size <= 0:
        return "", ()
    block_name = (CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(pos, dim) or {}).get("name") or ""
    if not block_name:
        return "", ()
    slots = _filter_machine_slots_for_access(
        dim, pos, access_facing, tuple(py2_xrange(size)), is_input
    )
    return block_name, slots


def read_slot(dim, pos, slot, is_chest):
    # type: (int, tuple[int, int, int], int, bool) -> tuple[Item | None, dict | None]
    if is_chest:
        raw = CF.CreateItem(LEVEL_ID).GetContainerItem(pos, slot, dim, True)
        if raw is None:
            return None, None
        item = Item.from_dict(raw)
        snapshot = deepcopy(raw)
    else:
        _, entries = _get_container_nbt(dim, pos, {})
        _, entry = _find_slot_entry(entries, slot)
        if entry is None:
            return None, None
        item = _nbt_entry_to_item(entry)
        snapshot = deepcopy(entry)
    if item.count <= 0 or item.id in ("", "minecraft:air"):
        return None, None
    return item, snapshot


def write_slot(dim, pos, slot, block_name, snapshot, item):
    # type: (int, tuple[int, int, int], int, str, dict | None, Item | None) -> bool
    "仅在快照匹配时修改同种物品的数量、插入空槽或清空槽位。"
    blocks = CF.CreateBlockInfo(LEVEL_ID)
    if (blocks.GetBlockNew(pos, dim) or {}).get("name") != block_name:
        return False
    if block_name in CHEST_CONTAINERS:
        _, current = read_slot(dim, pos, slot, True)
        if current != snapshot:
            return False
        success = CF.CreateItem(LEVEL_ID).SpawnItemToContainer(
            (item or Item("minecraft:air", count=0)).marshal(), slot, pos, dim
        )
    else:
        # 重新读取完整 NBT，保留事件回调对其他槽位的改动。
        data, entries = _get_container_nbt(dim, pos, {})
        if data is None:
            return False
        index, current = _find_slot_entry(entries, slot)
        if current is not None:
            current_item = _nbt_entry_to_item(current)
            if current_item.count <= 0 or current_item.id in ("", "minecraft:air"):
                current = None
        if current != snapshot:
            return False
        if item is None:
            if index >= 0:
                entries.pop(index)
        elif current is not None:
            current["Count"] = Byte(item.count)
        elif index >= 0:
            entries[index] = _item_to_nbt_entry(slot, item)
        else:
            entries.append(_item_to_nbt_entry(slot, item))
        success = blocks.SetBlockEntityData(dim, pos, data)
    InvalidateContainerCaches(dim, pos)
    return bool(success)
