# coding=utf-8
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item
from skybluetech_scripts.tooldelta.api.server import GetPlayerGameType
from skybluetech_scripts.tooldelta.events.server import (
    ServerPlayerTryDestroyBlockEvent,
)
from skybluetech_scripts.tooldelta.api.server import SpawnDroppedItem
from ...common.define import id_enum

GameType = GetMinecraftEnum().GameType

CARDINAL_BLOCKS = id_enum.Machinery.all() | {id_enum.RESIN_COLLECTOR, id_enum.FAMICOM}


@ServerPlayerTryDestroyBlockEvent.Listen()
def onTryDestroyBlock(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    # TODO: BUG: 不需要正确的工具也能挖机器
    if event.fullName in CARDINAL_BLOCKS:
        if GetPlayerGameType(event.playerId) == GameType.Creative:
            return
        event.spawnResources = False
        SpawnDroppedItem(
            event.dimensionId,
            (event.x + 0.5, event.y + 0.5, event.z + 0.5),
            Item(event.fullName),
        )
