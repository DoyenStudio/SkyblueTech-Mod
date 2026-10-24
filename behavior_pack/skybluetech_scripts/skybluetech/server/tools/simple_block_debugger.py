# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item
#
from skybluetech_scripts.tooldelta.events.server.block import ServerPlayerTryDestroyBlockEvent


@ServerPlayerTryDestroyBlockEvent.Listen()
def onBlockUse(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    mainhandItem = CF.CreateItem(event.playerId).GetPlayerItem(
        GetMinecraftEnum().ItemPosType.CARRIED,
        0,
        True,
    )
    mainhandItem = Item.from_dict(mainhandItem) if mainhandItem is not None else None
    if mainhandItem is None:
        return
    if mainhandItem.newItemName == "skybluetech:simple_block_debugger":
        _block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
            (event.x, event.y, event.z),
            event.dimensionId,
        )
        blockName, blockAux = (None, 0) if _block_data is None else (_block_data["name"], _block_data["aux"])
        if blockName is None:
            return
        tags = set(CF.CreateBlockInfo(LEVEL_ID).GetBlockTags(blockName))
        states = CF.CreateBlockState(LEVEL_ID).GetBlockStates(
            (event.x, event.y, event.z),
            event.dimensionId,
        )
        output = (
            "§a方块 ID: §f"
            + blockName
            + " §r§f特殊值： "
            + str(blockAux)
            + " [%s]" % bin(blockAux)
            + "\n"
            + "§e方块标签: §f"
            + ", ".join(tags)
            + "\n"
            + "§d方块状态: §f"
            + ", ".join(k + "=" + repr(v) for k, v in states.items())
        )
        CF.CreateGame(LEVEL_ID).SetOnePopupNotice(event.playerId, output, "§6方块基本数据")
        event.cancel()
        
