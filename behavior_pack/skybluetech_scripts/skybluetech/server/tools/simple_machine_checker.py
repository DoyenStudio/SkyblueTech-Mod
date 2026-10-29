# coding=utf-8
from skybluetech_scripts.tooldelta.srv import CF, LEVEL_ID
from mod.server.extraServerApi import GetMinecraftEnum
from skybluetech_scripts.tooldelta.define import Item
#
from skybluetech_scripts.tooldelta.events.server.block import (
    ServerPlayerTryDestroyBlockEvent,
)


from ..machinery.basic import GUIControl, MultiFluidContainer
from ..machinery.core.pool import GetLoadedMachine


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
    if mainhandItem.newItemName == "skybluetech:simple_machine_checker":
        m = GetLoadedMachine(event.dimensionId, event.x, event.y, event.z)
        if m is None:
            CF.CreateGame(LEVEL_ID).SetOnePopupNotice(
                event.playerId,
                "此方块 (%d, %d, %d) 不是机器" % (event.x, event.y, event.z),
                "§6提示§f",
            )
        else:
            if isinstance(m, GUIControl):
                m.CallSync()
            CF.CreateGame(LEVEL_ID).SetOnePopupNotice(event.playerId, "此方块 (%d, %d, %d) 是 %s ~%d"
                % (
                    event.x,
                    event.y,
                    event.z,
                    m.__class__.__name__,
                    m.deactive_flags,
                ), "§6提示§f")
        event.cancel()
        # extras
        if isinstance(m, MultiFluidContainer):
            all_slots = sorted(m.fluids)
            last_idx = len(all_slots) - 1
            for i, slot in enumerate(all_slots):
                m._on_fluid_slot_update(slot, i == last_idx)
