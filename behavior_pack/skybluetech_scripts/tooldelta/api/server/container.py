# coding=utf-8
from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId
from ...define.item import Item
from ..common.cacher import MethodCacher

CF = GetEngineCompFactory()

_getContainerItem = MethodCacher(lambda: CF.CreateItem(GetLevelId()).GetContainerItem)
_spawnItemToContainer = MethodCacher(
    lambda: CF.CreateItem(GetLevelId()).SpawnItemToContainer
)
_getContainerSize = MethodCacher(lambda: CF.CreateItem(GetLevelId()).GetContainerSize)
_setChestBoxItemNum = MethodCacher(
    lambda: CF.CreateChestBlock(GetLevelId()).SetChestBoxItemNum
)


def GetContainerItem(dim, pos, slotPos, getUserData=False):
    # type: (int, tuple[int, int, int], int, bool) -> Item | None
    res = _getContainerItem(pos, slotPos, dim, getUserData)
    if res is None:
        return None
    else:
        return Item.from_dict(res)


def SetContainerItem(dim, pos, slotPos, item):
    # type: (int, tuple[int, int, int], int, Item) -> bool
    return _spawnItemToContainer(item.marshal(), slotPos, pos, dim)


def PutItemIntoContainer(dim, pos, item, specific_slots=None):
    # type: (int, tuple[int, int, int], Item, tuple[int, ...] | None) -> Item | None
    "尝试将物品放入容器, 返回 None 表示物品已完全放入容器, 返回物品对象表示剩余物品。"
    if specific_slots is None:
        slots = range(GetContainerSize(pos, dim))
    else:
        slots = specific_slots
    for slot in slots:
        slotitem = GetContainerItem(dim, pos, slot)
        if slotitem is None:
            SetContainerItem(dim, pos, slot, item)
            return None
        elif slotitem.StackFull():
            continue
        elif slotitem.CanMerge(item):
            require_count = min(
                item.GetBasicInfo().maxStackSize - slotitem.count, item.count
            )
            slotitem.count += require_count
            item.count -= require_count
            SetContainerItem(dim, pos, slot, slotitem)
            if item.count == 0:
                return None
    return item


GetContainerSize = _getContainerSize  # redirect to fastboot func
SetChestBoxItemNum = _setChestBoxItemNum  # redirect to fastboot func

__all__ = [
    "GetContainerItem",
    "SetContainerItem",
    "GetContainerSize",
    "SetChestBoxItemNum",
    "PutItemIntoContainer",
]
