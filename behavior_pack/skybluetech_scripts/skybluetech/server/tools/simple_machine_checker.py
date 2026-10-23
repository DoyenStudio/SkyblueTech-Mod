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
from ..machinery.basic import GUIControl, MultiFluidContainer
from ..machinery.core.pool import GetLoadedMachine


@ServerPlayerTryDestroyBlockEvent.Listen()
def onBlockUse(event):
    # type: (ServerPlayerTryDestroyBlockEvent) -> None
    mainhandItem = GetPlayerMainhandItem(event.playerId)
    if mainhandItem is None:
        return
    if mainhandItem.newItemName == "skybluetech:simple_machine_checker":
        m = GetLoadedMachine(event.dimensionId, event.x, event.y, event.z)
        if m is None:
            SetOnePopupNotice(
                event.playerId,
                "此方块 (%d, %d, %d) 不是机器" % (event.x, event.y, event.z),
            )
        else:
            if isinstance(m, GUIControl):
                m.CallSync()
            SetOnePopupNotice(
                event.playerId,
                "此方块 (%d, %d, %d) 是 %s ~%d"
                % (
                    event.x,
                    event.y,
                    event.z,
                    m.__class__.__name__,
                    m.deactive_flags,
                ),
            )
        event.cancel()
        # extras
        if isinstance(m, MultiFluidContainer):
            all_slots = sorted(m.fluids)
            last_idx = len(all_slots) - 1
            for i, slot in enumerate(all_slots):
                m._on_fluid_slot_update(slot, i == last_idx)
