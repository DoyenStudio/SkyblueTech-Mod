# coding=utf-8
#
from mod.server import extraServerApi as serverApi
from ... import ServerComp
from ...define.item import Item

mcEnum = serverApi.GetMinecraftEnum()


def GetNameById(player_id):
    # type: (str) -> str
    return ServerComp.CreateName(player_id).GetName()

def GetPlayerDimensionId(player_id):
    # type: (str) -> int
    return ServerComp.CreateDimension(player_id).GetEntityDimensionId()

def SpawnItemToPlayerCarried(player_id, item):
    # type: (str, Item) -> None
    ServerComp.CreateItem(player_id).SpawnItemToPlayerCarried(item.marshal(), player_id)

def GiveItem(player_id, item):
    # type: (str, Item) -> None
    ServerComp.CreateItem(player_id).SpawnItemToPlayerInv(item.marshal(), player_id)

def GetAllPlayers():
    # type: () -> list[str]
    return serverApi.GetPlayerList()

def GetPlayersInDim(dim):
    # type: (int) -> list[str]
    return [player_id for player_id in GetAllPlayers() if GetPlayerDimensionId(player_id) == dim]

def GetPlayerMainhandItem(player_id):
    # type: (str) -> Item | None
    it = ServerComp.CreateItem(player_id).GetPlayerItem(mcEnum.ItemPosType.CARRIED, 0, True)
    if it is None:
        return None
    return Item.from_dict(it)

def GetSelectedSlot(player_id):
    # type: (str) -> int
    return ServerComp.CreateItem(player_id).GetSelectSlotId()

def SetInventorySlotItemCount(player_id, slot_id, count):
    # type: (str, int, int) -> bool
    return ServerComp.CreateItem(player_id).SetInvItemNum(slot_id, count)


__all__ = [
    "GetAllPlayers",
    "GetNameById",
    "GetPlayerDimensionId",
    "GetPlayerMainhandItem",
    "GetSelectedSlot",
    "GetPlayersInDim",
    "SetInventorySlotItemCount",
    "SpawnItemToPlayerCarried",
]