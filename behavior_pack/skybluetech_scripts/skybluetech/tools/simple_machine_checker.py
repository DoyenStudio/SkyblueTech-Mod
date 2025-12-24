# coding=utf-8
#
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlayerTryDestroyBlockEvent,
)
from skybluetech_scripts.tooldelta.api.server.block import (
    GetBlockNameAndAux,
    GetBlockTags,
    GetBlockStates,
)
from skybluetech_scripts.tooldelta.api.server.player import GetPlayerMainhandItem
from skybluetech_scripts.tooldelta.api.server.tips import SetOnePopupNotice
from ..machinery.basic import GUIControl
from ..machinery.pool import GetMachineStrict


@ServerPlayerTryDestroyBlockEvent.Listen()
def onBlockUse(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    mainhandItem = GetPlayerMainhandItem(event.playerId)
    if mainhandItem is None:
        return
    if mainhandItem.newItemName == "skybluetech:simple_machine_checker":
        m = GetMachineStrict(event.dimensionId, event.x, event.y, event.z)
        if m is None:
            SetOnePopupNotice(
                event.playerId,
                "此方块 (%d, %d, %d) 不是机器" % (event.x, event.y, event.z),
            )
        else:
            if isinstance(m, GUIControl):
                m.OnSync()
            m.Dump()
            if not m.is_non_energy_machine:
                networks_num = len([i for i in m.rf_networks if i])
            SetOnePopupNotice(
                event.playerId,
                "此方块 (%d, %d, %d) 是 %s [#%d]"
                % (
                    event.x,
                    event.y,
                    event.z,
                    m.__class__.__name__,
                    networks_num,
                ),
            )
        event.cancel()
