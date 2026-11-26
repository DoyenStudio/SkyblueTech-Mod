# coding=utf-8
from copy import deepcopy

from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from skybluetech_scripts.tooldelta.utils.py_comp import py2_xrange
from skybluetech_scripts.skybluetech.server.container_items import (
    GetContainerItem,
    SetContainerItem,
)
from skybluetech_scripts.skybluetech.server.transmitters.item_pipe.logic import (
    InvalidateContainerCaches,
    _filter_machine_slots_for_access,
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


def read_slot(dim, pos, slot):
    # type: (int, tuple[int, int, int], int) -> tuple[Item | None, dict | None]
    raw = GetContainerItem(pos, slot, dim, True)
    if raw is None:
        return None, None
    item = Item.from_dict(raw)
    snapshot = deepcopy(raw)
    if item.count <= 0 or item.id in ("", "minecraft:air"):
        return None, None
    return item, snapshot


def write_slot(dim, pos, slot, block_name, snapshot, item):
    # type: (int, tuple[int, int, int], int, str, dict | None, Item | None) -> bool
    "仅在快照匹配时修改同种物品的数量、插入空槽或清空槽位。"
    blocks = CF.CreateBlockInfo(LEVEL_ID)
    if (blocks.GetBlockNew(pos, dim) or {}).get("name") != block_name:
        return False
    _, current = read_slot(dim, pos, slot)
    if current != snapshot:
        return False
    success = SetContainerItem(pos, slot, dim, item)
    InvalidateContainerCaches(dim, pos)
    return bool(success)
