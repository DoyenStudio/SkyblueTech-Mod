# coding=utf-8
from skybluetech_scripts.tooldelta.api.server import GetBlockEntityDataDict
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.utils.nbt import (
    Byte,
    NBT2Py,
    Py2NBT,
    Short,
    String,
    GetValueWithDefault,
)

MISSING = type("_MISSING", (), {})()


def _get_nbt_scalar(nbt, default=None):
    # type: (dict | None, object) -> object
    "从 NBT 叶子节点提取原始值"
    if not isinstance(nbt, dict):
        return nbt if nbt is not None else default
    return nbt.get("__value__", default)


def _find_slot_entry(items, slot):
    # type: (list[dict], int) -> tuple[int, dict | None]
    "在容器 NBT 的 Items 列表中按 Slot 查找物品条目, 返回 (列表下标, 条目)"
    for i, item in enumerate(items):
        if _get_nbt_scalar(item.get("Slot"), -1) == slot:
            return i, item
    return -1, None


def _nbt_entry_to_item(entry):
    # type: (dict) -> Item
    "将容器 NBT 中的物品条目转换为 Item"
    item = Item(
        _get_nbt_scalar(entry.get("Name"), ""),
        _get_nbt_scalar(entry.get("Damage"), 0),
        _get_nbt_scalar(entry.get("Count"), 0),
    )
    tag = entry.get("tag")
    if tag:
        item.userData = NBT2Py(tag)
    return item


def _item_to_nbt_entry(slot, item):
    # type: (int, Item) -> dict
    "将 Item 转换为容器 NBT 中的物品条目 (用于新条目)"
    entry = {
        "Count": Byte(item.count),
        "Slot": Byte(slot),
        "Name": String(item.newItemName),
        "Damage": Short(item.newAuxValue),
        "WasPickedUp": Byte(0),
    }
    if item.userData is not None:
        entry["tag"] = Py2NBT(item.userData)
    return entry


def _get_container_nbt(dim, xyz, cache_datas):
    # type: (int, tuple[int, int, int], dict[tuple[int, int, int], dict | None]) -> tuple[dict | None, list[dict]]
    "读取容器的一整个 NBT, 缓存由调用方传入并在内容变化时负责失效; 返回 (data, Items 列表)"
    data = cache_datas.get(xyz, MISSING)
    if data is MISSING:
        data = cache_datas[xyz] = GetBlockEntityDataDict(dim, xyz)
    if data is None:
        return None, []
    items = data.get("Items")
    if items is None:
        items = data["Items"] = []
    return data, items
