# coding=utf-8
#
from skybluetech_scripts.tooldelta.events.server.block import ServerPlayerTryDestroyBlockEvent
from skybluetech_scripts.tooldelta.api.server.block import GetBlockNameAndAux, GetBlockTags, GetBlockStates
from skybluetech_scripts.tooldelta.api.server.player import GetPlayerMainhandItem
from skybluetech_scripts.tooldelta.api.server.tips import SetOnePopupNotice

@ServerPlayerTryDestroyBlockEvent.Listen()
def onBlockUse(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    mainhandItem = GetPlayerMainhandItem(event.playerId)
    if mainhandItem is None:
        return
    if mainhandItem.newItemName == "skybluetech:simple_block_debugger":
        blockName, blockAux = GetBlockNameAndAux(event.dimensionId, (event.x, event.y, event.z))
        if blockName is None:
            return
        tags = GetBlockTags(blockName)
        states = GetBlockStates(event.dimensionId, (event.x, event.y, event.z))
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
        SetOnePopupNotice(event.playerId, output, "§6方块基本数据")
        event.cancel()
        
