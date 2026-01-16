# coding=utf-8
#
from ...define import itemBasicInfoPool, BasicItemInfo, Item
from ...internal import ServerComp, ServerLevelId

if 0:
    from typing import Callable

_lookupItemByName = ServerComp.CreateGame(ServerLevelId).LookupItemByName
_setItemTierSpeed = ServerComp.CreateItem(ServerLevelId).SetItemTierSpeed
_setAttackDamage = ServerComp.CreateItem(ServerLevelId).SetAttackDamage

ItemExists = _lookupItemByName

def GetItemBasicInfo(itemName):
    # type: (str) -> BasicItemInfo
    basic_info = itemBasicInfoPool.get(itemName)
    if basic_info is not None:
        return basic_info
    basic_info = BasicItemInfo().unmarshal(
        ServerComp.CreateItem(ServerLevelId).GetItemBasicInfo(itemName)
    )
    itemBasicInfoPool[itemName] = basic_info
    return basic_info

def SetItemTierSpeed(item, speed):
    # type: (Item, float) -> bool
    item_dict = item.marshal()
    res = _setItemTierSpeed(item_dict, speed)
    # ud = item.userData
    # if ud is None:
    #     print("[SkyBlueTech] SetItemTierSpeed: item userdata is None")
    #     return False
    # ud["ModTierSpeed"] = {"__type__": 5, "__value__": speed}
    # return True
    item.unmarshal(item_dict)
    return res

def SetAttackDamage(item, damage):
    # type: (Item, int) -> bool
    item_dict = item.marshal()
    res = _setAttackDamage(item_dict, damage)
    item.unmarshal(item_dict)
    return res

def GetPlayerUIItem(player_id, slot, get_user_data=False, is_netease_ui=False):
    # type: (str, int, bool, bool) -> Item
    return Item.from_dict(
        ServerComp.CreateItem(ServerLevelId).GetPlayerUIItem(
            player_id, slot, get_user_data, is_netease_ui
        )
    )

def SpawnItemToPlayerInv(player_id, item):
    # type: (str, Item) -> None
    ServerComp.CreateItem(ServerLevelId).SpawnItemToPlayerInv(item.marshal(), player_id)

def SetPlayerUIItem(player_id, slot, item, need_back=False, is_netease_ui=False):
    # type: (str, int, Item, bool, bool) -> None
    ServerComp.CreateItem(ServerLevelId).SetPlayerUIItem(
        player_id, slot, item.marshal(), need_back, is_netease_ui
    )

def SortItems(items, key=lambda i: i.id):
    # type: (list[Item], Callable[[Item], str | int]) -> list[Item]
    its = {} # type: dict[str, list[Item]]
    max_stacks = {} # type: dict[str, int]
    for item in items:
        if item.id not in its:
            its[item.id] = []
            max_stacks[item.id] = item.GetBasicInfo().maxStackSize
        its[item.id].append(item)
    res = [] # type: list[Item]
    for items in sorted(its.values(), key=lambda x: key(x[0])):
        i_res = [] # type: list[Item]
        for item in items:
            for item_2 in i_res:
                if item_2.CanMerge(item):
                    sum_count = item_2.count + item.count
                    max_stack = max_stacks[item.id]
                    if sum_count <= max_stack:
                        item_2.count = sum_count
                        item = None
                        break
                    else:
                        item.count -= sum_count - max_stack
                        item_2.count = max_stack
            if item is not None:
                i_res.append(item)
        res.extend(i_res)
    return res


__all__ = [
    "ItemExists",
    "GetItemBasicInfo",
    "SetItemTierSpeed",
    "GetPlayerUIItem",
    "SpawnItemToPlayerInv",
    "SetPlayerUIItem",
    "SetAttackDamage",
    "SortItems",
]
