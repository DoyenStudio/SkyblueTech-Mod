# coding=utf-8
"""容器槽位只通过引擎物品接口读写，不解析方块实体的 Items。"""
from skybluetech_scripts.tooldelta.define.item import Item
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID


def GetContainerItem(pos, slot, dim, get_user_data=True):
    # type: (tuple[int, int, int], int, int, bool) -> dict | None
    return CF.CreateItem(LEVEL_ID).GetContainerItem(pos, slot, dim, get_user_data)


def SetContainerItem(pos, slot, dim, item):
    # type: (tuple[int, int, int], int, int, Item | None) -> bool
    # 当前 ModAPI 的容器写入接口名称为 SpawnItemToContainer。
    if item is None or item.count <= 0:
        item = Item("minecraft:air", count=0)
    return CF.CreateItem(LEVEL_ID).SpawnItemToContainer(item.marshal(), slot, pos, dim)
