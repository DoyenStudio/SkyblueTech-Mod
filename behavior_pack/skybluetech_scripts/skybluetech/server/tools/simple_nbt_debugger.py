# coding=utf-8
#
import json
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlayerTryDestroyBlockEvent,
)
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockNameAndAux,
    GetBlockEntityDataDict,
)
from skybluetech_scripts.tooldelta.api.server.player import GetPlayerMainhandItem
from skybluetech_scripts.tooldelta.api.server.tips import NotifyOneMessage


@ServerPlayerTryDestroyBlockEvent.Listen()
def onBlockUse(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    mainhandItem = GetPlayerMainhandItem(event.playerId)
    if mainhandItem is None:
        return
    if mainhandItem.newItemName == "skybluetech:simple_blocknbt_debugger":
        blockName, blockAux = GetBlockNameAndAux(
            event.dimensionId, (event.x, event.y, event.z)
        )
        if blockName is None:
            return
        nbts = GetBlockEntityDataDict(event.dimensionId, event.x, event.y, event.z)
        output = (
            "§a方块 ID: §f"
            + blockName
            + " §r§f特殊值： "
            + str(blockAux)
            + "\n"
            + "§e方块数据: §f"
        )
        output_jsons = json.dumps(nbts, indent=4, ensure_ascii=False).split("\n")
        NotifyOneMessage(event.playerId, output)
        for i in range(0, len(output_jsons), 10):
            NotifyOneMessage(
                event.playerId, "§7：§f " + "\n§7：§f ".join(output_jsons[i : i + 10])
            )
        event.cancel()
