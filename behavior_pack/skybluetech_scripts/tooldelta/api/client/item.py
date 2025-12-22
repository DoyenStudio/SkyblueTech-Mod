# coding=utf-8
#
from ...internal import ClientComp, ClientLevelId

item_tags_pool = {} # type: dict[str, set[str]]

def GetItemHoverName(itemName):
    # type: (str) -> str
    return ClientComp.CreateItem(ClientLevelId).GetItemHoverName(itemName)

def GetItemTags(item_id, aux_value=0):
    # type: (str, int) -> set[str]
    basic_info = item_tags_pool.get(item_id)
    if basic_info is not None:
        return basic_info
    tags = set(ClientComp.CreateItem(ClientLevelId).GetItemTags(item_id, aux_value))
    item_tags_pool[item_id] = tags
    return tags


__all__ = [
    "GetItemHoverName",
    "GetItemTags",
]
