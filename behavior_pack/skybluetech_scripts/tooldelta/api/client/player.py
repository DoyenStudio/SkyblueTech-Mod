# coding=utf-8
#
from mod.client import extraClientApi as clientApi
from ...define.item import Item
from ... import ClientComp
from ...internal import inClientEnv

mcEnum = clientApi.GetMinecraftEnum()


def GetNameById(player_id):
    # type: (str) -> str
    return ClientComp.CreateName(player_id).GetName()

def GetPlayerDimensionId():
    # type: () -> int
    return ClientComp.CreateGame(GetLocalPlayerId()).GetCurrentDimension()

def GetAllPlayers():
    # type: () -> list[str]
    return clientApi.GetPlayerList()

def GetLocalPlayerId():
    if not inClientEnv():
        raise Exception("Not in client env")
    return clientApi.GetLocalPlayerId()

def GetPlayerMainhandItem(player_id):
    # type: (str) -> Item | None
    it = ClientComp.CreateItem(player_id).GetPlayerItem(mcEnum.ItemPosType.CARRIED, 0, True)
    if it is None:
        return None
    return Item("").unmarshal(it)




__all__ = [
    "GetNameById",
    "GetPlayerDimensionId",
    "GetAllPlayers",
    "GetLocalPlayerId",
    "GetPlayerMainhandItem",
]