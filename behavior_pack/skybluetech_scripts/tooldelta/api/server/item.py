# coding=utf-8
#
from mod.server.extraServerApi import GetEngineCompFactory, GetLevelId
from ...define import itemBasicInfoPool, BasicItemInfo, Item
from ..common.cacher import MethodCacher

if 0:
    from typing import Callable

CF = GetEngineCompFactory()

_lookupItemByName = MethodCacher(lambda: CF.CreateGame(GetLevelId()).LookupItemByName)
_setItemTierSpeed = MethodCacher(lambda: CF.CreateItem(GetLevelId()).SetItemTierSpeed)
_setAttackDamage = MethodCacher(lambda: CF.CreateItem(GetLevelId()).SetAttackDamage)

ItemExists = _lookupItemByName


def GetItemBasicInfo(itemName):
    # type: (str) -> BasicItemInfo
    basic_info = itemBasicInfoPool.get(itemName)
    if basic_info is not None:
        return basic_info
    basic_info = BasicItemInfo().unmarshal(
        CF.CreateItem(GetLevelId()).GetItemBasicInfo(itemName)
    )
    itemBasicInfoPool[itemName] = basic_info
    return basic_info


item_tags_pool = {}  # type: dict[str, set[str]]


def GetItemTags(item_id, aux_value=0):
    # type: (str, int) -> set[str]
    basic_info = item_tags_pool.get(item_id)
    if basic_info is not None:
        return basic_info
    tags = set(CF.CreateItem(GetLevelId()).GetItemTags(item_id, aux_value))
    item_tags_pool[item_id] = tags
    return tags


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
    # type: (str, int, bool, bool) -> Item | None
    res = CF.CreateItem(GetLevelId()).GetPlayerUIItem(
        player_id, slot, get_user_data, is_netease_ui
    )
    return Item.from_dict(res) if res is not None else None


def SpawnItemToPlayerInv(player_id, item):
    # type: (str, Item) -> None
    CF.CreateItem(GetLevelId()).SpawnItemToPlayerInv(item.marshal(), player_id)


def SetPlayerUIItem(player_id, slot, item, need_back=False, is_netease_ui=False):
    # type: (str, int, Item, bool, bool) -> None
    CF.CreateItem(GetLevelId()).SetPlayerUIItem(
        player_id, slot, item.marshal(), need_back, is_netease_ui
    )


__all__ = [
    "ItemExists",
    "GetItemBasicInfo",
    "GetItemTags",
    "GetPlayerUIItem",
    "SetItemTierSpeed",
    "SpawnItemToPlayerInv",
    "SetPlayerUIItem",
    "SetAttackDamage",
]
