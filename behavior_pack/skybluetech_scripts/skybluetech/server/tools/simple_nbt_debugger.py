# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item
#
import json
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlayerTryDestroyBlockEvent,
)


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
    if mainhandItem.newItemName == "skybluetech:simple_blocknbt_debugger":
        _block_data = CF.CreateBlockInfo(LEVEL_ID).GetBlockNew(
            (event.x, event.y, event.z),
            event.dimensionId,
        )
        blockName, blockAux = (None, 0) if _block_data is None else (_block_data["name"], _block_data["aux"])
        if blockName is None:
            return
        nbts = CF.CreateBlockInfo(LEVEL_ID).GetBlockEntityData(
            event.dimensionId,
            (event.x, event.y, event.z),
        )
        output = (
            "§a方块 ID: §f"
            + blockName
            + " §r§f特殊值： "
            + str(blockAux)
            + "\n"
            + "§e方块数据: §f"
        )
        output_jsons = json.dumps(nbts, indent=4, ensure_ascii=False).split("\n")
        CF.CreateMsg(LEVEL_ID).NotifyOneMessage(event.playerId, output)
        for i in range(0, len(output_jsons), 10):
            CF.CreateMsg(LEVEL_ID).NotifyOneMessage(
                event.playerId,
                "§7：§f " + "\n§7：§f ".join(output_jsons[i : i + 10]),
            )
        event.cancel()
