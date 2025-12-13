# coding=utf-8
#
from skybluetech_scripts.tooldelta.events.server.block import ServerPlayerTryDestroyBlockEvent
from skybluetech_scripts.tooldelta.api.server.block import GetBlockNameAndAux, GetBlockTags, GetBlockStates
from skybluetech_scripts.tooldelta.api.server.player import GetPlayerMainhandItem
from skybluetech_scripts.tooldelta.api.server.tips import SetOnePopupNotice
from ..machines.pool import GetMachineStrict

@ServerPlayerTryDestroyBlockEvent.Listen()
def onBlockUse(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    mainhandItem = GetPlayerMainhandItem(event.playerId)
    if mainhandItem is None:
        return
    if mainhandItem.newItemName == "skybluetech:simple_machine_checker":
        m = GetMachineStrict(event.dimensionId, event.x, event.y, event.z)
        if m is None:
            SetOnePopupNotice(event.playerId, "此方块 (%d, %d, %d) 不是机器" % (event.x, event.y, event.z))
        else:
            SetOnePopupNotice(event.playerId, "此方块 (%d, %d, %d) 是 %s" % (event.x, event.y, event.z, m.__class__.__name__))
        event.cancel()
